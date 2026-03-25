# tracking/focus_mode.py
"""
Focus mode manager - blocks distracting apps and websites during focus sessions.
"""

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

from database.connection import DatabasePool
from database.models import FocusSettings
from database.repositories.focus_settings_repo import FocusSettingsRepository
from tracking.website_blocker import WebsiteBlocker
from utils.logger import setup_logger
from utils.platform_utils import get_active_window_title, minimize_window

logger = setup_logger("tracking.focus_mode")


class AppBlockerWorker(QThread):
    """Background thread that monitors and blocks distracting apps."""

    app_blocked = pyqtSignal(str)

    def __init__(self, blocked_apps: list[str], parent: QObject = None) -> None:  # type: ignore[assignment]
        super().__init__(parent)
        self.blocked_apps = [app.strip().lower() for app in blocked_apps if app.strip()]
        self.is_active = False

    def run(self) -> None:
        self.is_active = True
        logger.info(f"App blocker started. Blocking: {self.blocked_apps}")

        while self.is_active:
            try:
                active_title = get_active_window_title()
                if active_title and active_title != "No Active Window":
                    title_lower = active_title.lower()
                    for app in self.blocked_apps:
                        if app in title_lower:
                            minimize_window(active_title)
                            self.app_blocked.emit(app)
                            logger.info(f"Blocked app: {app} (window: {active_title[:50]})")
                            break
            except Exception as e:
                logger.error(f"App blocker error: {e}")

            self.msleep(1000)

    def stop(self) -> None:
        self.is_active = False


class FocusModeManager(QObject):
    """
    Manages focus mode sessions including app and website blocking.
    """

    session_started = pyqtSignal()
    session_ended = pyqtSignal()
    app_blocked = pyqtSignal(str)
    time_remaining = pyqtSignal(int)

    def __init__(self, db_pool: DatabasePool, parent: QObject = None) -> None:  # type: ignore[assignment]
        super().__init__(parent)
        self.db_pool = db_pool
        self.focus_repo = FocusSettingsRepository(db_pool)
        self.website_blocker = WebsiteBlocker()
        self.app_blocker_worker: AppBlockerWorker | None = None
        self.is_active = False
        self.current_settings: FocusSettings | None = None

        # Timer for session countdown
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._on_countdown_tick)
        self._remaining_seconds = 0

    def start_session(self, settings: FocusSettings, duration_minutes: int = 25) -> None:
        """Start a new focus session."""
        if self.is_active:
            logger.warning("Focus session already active")
            return

        # Save settings to DB
        settings.is_active = True
        self.focus_repo.save_settings(settings)
        self.current_settings = settings

        # Block websites
        if settings.blocked_websites:
            success = self.website_blocker.block(settings.blocked_websites)
            if not success:
                logger.warning("Failed to block some websites (may need admin privileges)")

        # Start app blocker thread
        if settings.blocked_apps:
            self.app_blocker_worker = AppBlockerWorker(settings.blocked_apps)
            self.app_blocker_worker.app_blocked.connect(self.app_blocked.emit)
            self.app_blocker_worker.start()

        # Start countdown
        self._remaining_seconds = duration_minutes * 60
        self._countdown_timer.start(60 * 1000)

        self.is_active = True
        self.session_started.emit()
        logger.info(f"Focus session started for {duration_minutes} minutes")

    def end_session(self) -> None:
        """End the current focus session."""
        if not self.is_active:
            return

        # Stop app blocker
        if self.app_blocker_worker is not None and self.app_blocker_worker.isRunning():
            self.app_blocker_worker.stop()
            self.app_blocker_worker.wait(3000)

        # Unblock websites
        if self.current_settings is not None and self.current_settings.blocked_websites:
            self.website_blocker.unblock(self.current_settings.blocked_websites)

        # Update DB
        self.focus_repo.deactivate_all()

        # Stop countdown
        self._countdown_timer.stop()

        self.is_active = False
        self.current_settings = None
        self.session_ended.emit()
        logger.info("Focus session ended")

    def _on_countdown_tick(self) -> None:
        """Called every minute during focus session."""
        self._remaining_seconds -= 60
        self.time_remaining.emit(self._remaining_seconds)

        if self._remaining_seconds <= 0:
            self.end_session()

    def get_remaining_minutes(self) -> int:
        return max(0, self._remaining_seconds // 60)

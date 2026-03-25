# tracking/activity_tracker.py
"""
Core activity tracking engine.
Runs in a background QThread and logs active window information.
"""

import datetime

from PyQt5.QtCore import QThread, pyqtSignal

from config.settings import app_config
from database.connection import DatabasePool
from database.models import ActivityLog
from database.repositories.activity_repo import ActivityRepository
from tracking.categorizer import AppCategorizer
from utils.logger import setup_logger
from utils.platform_utils import get_active_window_title

logger = setup_logger("tracking.activity")


class ActivityTracker(QThread):
    """
    Background thread that tracks the active window at regular intervals.

    Signals:
        activity_logged(str): Emitted when a new activity is logged (formatted string).
        error_occurred(str): Emitted when an error occurs.
        tracking_status_changed(bool): Emitted when tracking starts/stops.
    """

    activity_logged = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    tracking_status_changed = pyqtSignal(bool)

    def __init__(self, db_pool: DatabasePool, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.activity_repo = ActivityRepository(db_pool)
        self.categorizer = AppCategorizer(db_pool)
        self.is_tracking = False
        self.interval = app_config.tracking_interval  # seconds
        self._last_window_title = ""
        self._last_change_time = datetime.datetime.now()

    def run(self):
        """Main tracking loop — runs in background thread."""
        self.is_tracking = True
        self.tracking_status_changed.emit(True)
        logger.info(f"Activity tracking started (interval: {self.interval}s)")

        while self.is_tracking:
            try:
                self._track_once()
            except Exception as e:
                logger.error(f"Tracking error: {e}", exc_info=True)
                self.error_occurred.emit(str(e))

            # Sleep in small increments so we can stop quickly
            for _ in range(self.interval * 10):
                if not self.is_tracking:
                    break
                self.msleep(100)  # 100ms intervals

        self.tracking_status_changed.emit(False)
        logger.info("Activity tracking stopped")

    def _track_once(self):
        """Track the current active window once."""
        current_time = datetime.datetime.now()
        window_title = get_active_window_title()

        # Skip if same window as before (we'll update duration instead)
        if window_title == self._last_window_title:
            return

        # Calculate duration for the previous window
        if self._last_window_title:
            duration = int((current_time - self._last_change_time).total_seconds())
            category = self.categorizer.categorize(self._last_window_title)

            activity = ActivityLog(
                timestamp=self._last_change_time,
                window_title=self._last_window_title,
                category=category,
                duration_seconds=duration,
            )
            self.activity_repo.log_activity(activity)

            # Emit signal for UI update
            log_msg = (
                f"{self._last_change_time.strftime('%H:%M:%S')} | "
                f"[{category.value.upper():^14}] | "
                f"{duration:>4}s | "
                f"{self._last_window_title[:60]}"
            )
            self.activity_logged.emit(log_msg)

        # Update tracking state
        self._last_window_title = window_title
        self._last_change_time = current_time

    def stop_tracking(self):
        """Stop the tracking loop gracefully."""
        logger.info("Stopping activity tracker...")
        self.is_tracking = False

    def set_interval(self, seconds: int):
        """Update tracking interval."""
        self.interval = max(1, seconds)
        logger.info(f"Tracking interval set to {self.interval}s")

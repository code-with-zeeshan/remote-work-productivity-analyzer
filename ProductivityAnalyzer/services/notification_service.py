# services/notification_service.py
"""
Desktop notification service using Qt's system tray.
"""

import os
import sys

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QStyle, QSystemTrayIcon

from config.settings import app_config
from utils.logger import setup_logger

logger = setup_logger("services.notification")


class NotificationService(QObject):
    """Manages desktop notifications and break reminders."""

    break_reminder_triggered = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)

        # Set icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            app = QApplication.instance()
            if app is not None and hasattr(app, "style"):
                style = app.style()  # type: ignore[union-attr]
                if style is not None:
                    self.tray_icon.setIcon(
                        style.standardIcon(QStyle.SP_ComputerIcon)  # type: ignore[attr-defined]
                    )

        self.tray_icon.setToolTip("ProductivityAnalyzer v2.0")
        self._setup_tray_menu()
        self.tray_icon.setVisible(True)

        # Break reminder timer
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self._on_break_reminder)
        self._break_interval = app_config.break_reminder_minutes * 60 * 1000

    def _setup_tray_menu(self) -> None:
        """Create the system tray context menu."""
        menu = QMenu()
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self._show_parent)
        menu.addAction(show_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def _show_parent(self) -> None:
        """Show the parent window."""
        p = self.parent()
        if p is not None and hasattr(p, "show"):
            p.show()  # type: ignore[union-attr]

    @staticmethod
    def _quit_app() -> None:
        """Quit the application."""
        sys.exit(0)

    def notify(self, title: str, message: str, duration: int = 5000) -> None:
        """Show a desktop notification."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,  # type: ignore[attr-defined]
                duration,
            )
            logger.debug(f"Notification: {title} - {message}")
        else:
            logger.warning(f"System tray not available. Notification: {title}")

    def start_break_reminders(self) -> None:
        """Start periodic break reminders."""
        self.break_timer.start(self._break_interval)
        logger.info(f"Break reminders started (every {app_config.break_reminder_minutes} min)")

    def stop_break_reminders(self) -> None:
        """Stop break reminders."""
        self.break_timer.stop()

    def _on_break_reminder(self) -> None:
        """Triggered when break reminder fires."""
        self.notify(
            "Break Time!",
            f"You've been working for {app_config.break_reminder_minutes} minutes. " "Take a short break!",
            duration=10000,
        )
        self.break_reminder_triggered.emit()

    def notify_focus_session_started(self, duration_minutes: int) -> None:
        self.notify(
            "Focus Mode Active",
            f"Focus session started for {duration_minutes} minutes. Stay focused!",
        )

    def notify_focus_session_ended(self) -> None:
        self.notify(
            "Focus Session Complete",
            "Great work! Your focus session has ended.",
        )

    def notify_goal_progress(self, goal_name: str, progress: float) -> None:
        if progress >= 100:
            self.notify("Goal Achieved!", f"Congratulations! You completed: {goal_name}")
        elif progress >= 75:
            self.notify(
                "Almost There!",
                f"{goal_name}: {progress:.0f}% complete. Keep going!",
            )

    def notify_export_complete(self, filepath: str) -> None:
        self.notify("Export Complete", f"Report saved to: {filepath}")

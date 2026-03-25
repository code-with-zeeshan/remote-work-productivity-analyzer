# ui/widgets/focus_mode_widget.py
"""
Focus Mode page — configure and control focus sessions.
"""

from datetime import time

from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtWidgets import (
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from database.connection import DatabasePool
from database.models import FocusSettings
from services.notification_service import NotificationService
from tracking.focus_mode import FocusModeManager
from utils.logger import setup_logger
from utils.validators import validate_blocked_list, validate_time_range

logger = setup_logger("ui.focus_mode")


class FocusModeWidget(QWidget):
    """Focus mode configuration and session control."""

    def __init__(
        self,
        db_pool: DatabasePool,
        focus_manager: FocusModeManager,
        notification_service: NotificationService,
        parent=None,
    ):
        super().__init__(parent)
        self.db_pool = db_pool
        self.focus_manager = focus_manager
        self.notification_service = notification_service
        self._build_ui()
        self._connect_signals()

        # UI update timer
        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._update_timer_display)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("🎯 Focus Mode")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Block distractions and stay focused during work sessions")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        # ── Status Card ──
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)

        self.status_label = QLabel("⚪ Focus Mode Inactive")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #636e72;")
        status_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #0984e3;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.timer_label)

        layout.addWidget(status_card)

        # ── Configuration Group ──
        config_group = QGroupBox("Session Configuration")
        config_layout = QFormLayout(config_group)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 180)
        self.duration_input.setValue(25)
        self.duration_input.setSuffix(" minutes")
        config_layout.addRow("Duration:", self.duration_input)

        self.start_time_input = QTimeEdit()
        self.start_time_input.setTime(QTime(9, 0))
        self.start_time_input.setDisplayFormat("HH:mm")
        config_layout.addRow("Focus Start Time:", self.start_time_input)

        self.end_time_input = QTimeEdit()
        self.end_time_input.setTime(QTime(17, 0))
        self.end_time_input.setDisplayFormat("HH:mm")
        config_layout.addRow("Focus End Time:", self.end_time_input)

        self.blocked_apps_input = QLineEdit()
        self.blocked_apps_input.setPlaceholderText("e.g., youtube, facebook, reddit (comma-separated)")
        config_layout.addRow("Block Apps:", self.blocked_apps_input)

        self.blocked_websites_input = QLineEdit()
        self.blocked_websites_input.setPlaceholderText("e.g., facebook.com, youtube.com (comma-separated)")
        config_layout.addRow("Block Websites:", self.blocked_websites_input)

        layout.addWidget(config_group)

        # ── Buttons ──
        button_row = QHBoxLayout()

        self.start_button = QPushButton("▶️  Start Focus Session")
        self.start_button.setObjectName("successButton")
        self.start_button.setFixedHeight(45)
        self.start_button.clicked.connect(self._start_session)
        button_row.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹️  End Session")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setFixedHeight(45)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_session)
        button_row.addWidget(self.stop_button)

        layout.addLayout(button_row)
        layout.addStretch()

    def _connect_signals(self):
        self.focus_manager.session_started.connect(self._on_session_started)
        self.focus_manager.session_ended.connect(self._on_session_ended)
        self.focus_manager.time_remaining.connect(self._on_time_update)

    def _start_session(self):
        """Validate inputs and start a focus session."""
        # Parse inputs
        start_qtime = self.start_time_input.time()
        end_qtime = self.end_time_input.time()
        start_time = time(start_qtime.hour(), start_qtime.minute())
        end_time = time(end_qtime.hour(), end_qtime.minute())

        valid, error = validate_time_range(start_time, end_time)
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return

        _, blocked_apps = validate_blocked_list(self.blocked_apps_input.text())
        _, blocked_websites = validate_blocked_list(self.blocked_websites_input.text())

        settings = FocusSettings(
            start_time=start_time,
            end_time=end_time,
            blocked_apps=blocked_apps,
            blocked_websites=blocked_websites,
        )

        duration = self.duration_input.value()
        self.focus_manager.start_session(settings, duration_minutes=duration)

    def _stop_session(self):
        """End the current focus session."""
        reply = QMessageBox.question(
            self,
            "End Focus Session",
            "Are you sure you want to end your focus session?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.focus_manager.end_session()

    def _on_session_started(self):
        self.status_label.setText("🟢 Focus Mode ACTIVE")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00b894;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._ui_timer.start(1000)
        logger.info("Focus session started (UI updated)")

    def _on_session_ended(self):
        self.status_label.setText("⚪ Focus Mode Inactive")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #636e72;")
        self.timer_label.setText("")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._ui_timer.stop()

        QMessageBox.information(self, "Session Complete", "🎉 Great work! Your focus session has ended.")
        logger.info("Focus session ended (UI updated)")

    def _on_time_update(self, remaining_seconds: int):
        self._update_timer_display()

    def _update_timer_display(self):
        remaining = self.focus_manager.get_remaining_minutes()
        minutes = remaining
        self.timer_label.setText(f"{minutes} min remaining")

    def refresh_data(self):
        pass  # No data to refresh on navigate

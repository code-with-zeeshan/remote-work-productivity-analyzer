# ui/main_window.py
"""
Main application window with sidebar navigation and stacked pages.
"""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.constants import SIDEBAR_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from config.settings import app_config
from database.connection import DatabasePool
from reporting.report_generator import ReportGenerator
from services.notification_service import NotificationService
from services.suggestion_engine import SuggestionEngine
from tracking.activity_tracker import ActivityTracker
from tracking.focus_mode import FocusModeManager
from ui.widgets.activity_log_widget import ActivityLogWidget
from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.focus_mode_widget import FocusModeWidget
from ui.widgets.goals_widget import GoalsWidget
from ui.widgets.reports_widget import ReportsWidget
from ui.widgets.settings_widget import SettingsWidget
from utils.logger import setup_logger

logger = setup_logger("ui.main_window")


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    PAGE_DASHBOARD = 0
    PAGE_ACTIVITY_LOG = 1
    PAGE_FOCUS_MODE = 2
    PAGE_REPORTS = 3
    PAGE_GOALS = 4
    PAGE_SETTINGS = 5

    def __init__(self, db_pool: DatabasePool, parent=None) -> None:
        super().__init__(parent)
        self.db_pool = db_pool

        # Initialize services
        self.activity_tracker = ActivityTracker(db_pool, parent=self)
        self.focus_manager = FocusModeManager(db_pool, parent=self)
        self.notification_service = NotificationService(parent=self)
        self.suggestion_engine = SuggestionEngine(db_pool)
        self.report_generator = ReportGenerator(db_pool)

        # Setup UI
        self.setWindowTitle(f"{app_config.app_name} v{app_config.version}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1200, 750)

        self._load_stylesheet()
        self._build_ui()
        self._connect_signals()

        # Start tracking on launch
        self.activity_tracker.start()
        self.notification_service.start_break_reminders()

        logger.info("Main window initialized")

    def _load_stylesheet(self) -> None:
        """Load the QSS stylesheet with explicit UTF-8 encoding."""
        style_path = os.path.join(os.path.dirname(__file__), "styles", "style.qss")
        try:
            with open(style_path, encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            logger.warning(f"Stylesheet not found: {style_path}")
        except Exception as e:
            logger.warning(f"Error loading stylesheet: {e}")

    def _build_ui(self) -> None:
        """Build the main layout with sidebar + stacked content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")

        # Create page widgets
        self.dashboard_widget = DashboardWidget(
            db_pool=self.db_pool,
            report_gen=self.report_generator,
            suggestion_engine=self.suggestion_engine,
            parent=self,
        )
        self.activity_log_widget = ActivityLogWidget(db_pool=self.db_pool, parent=self)
        self.focus_mode_widget = FocusModeWidget(
            db_pool=self.db_pool,
            focus_manager=self.focus_manager,
            notification_service=self.notification_service,
            parent=self,
        )
        self.reports_widget = ReportsWidget(db_pool=self.db_pool, parent=self)
        self.goals_widget = GoalsWidget(db_pool=self.db_pool, parent=self)
        self.settings_widget = SettingsWidget(
            db_pool=self.db_pool,
            tracker=self.activity_tracker,
            parent=self,
        )

        # Add pages to stack
        self.content_stack.addWidget(self.dashboard_widget)
        self.content_stack.addWidget(self.activity_log_widget)
        self.content_stack.addWidget(self.focus_mode_widget)
        self.content_stack.addWidget(self.reports_widget)
        self.content_stack.addWidget(self.goals_widget)
        self.content_stack.addWidget(self.settings_widget)

        main_layout.addWidget(self.content_stack)

    def _build_sidebar(self) -> QFrame:
        """Build the sidebar navigation panel."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App title
        title_label = QLabel(f"  {app_config.app_name}")
        title_label.setObjectName("sidebarTitle")
        title_label.setFixedHeight(60)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        sidebar_layout.addWidget(title_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("sidebarSeparator")
        sidebar_layout.addWidget(line)

        # Navigation buttons
        nav_items = [
            ("  Dashboard", self.PAGE_DASHBOARD),
            ("  Activity Log", self.PAGE_ACTIVITY_LOG),
            ("  Focus Mode", self.PAGE_FOCUS_MODE),
            ("  Reports", self.PAGE_REPORTS),
            ("  Goals", self.PAGE_GOALS),
            ("  Settings", self.PAGE_SETTINGS),
        ]

        self.nav_buttons = []
        for label, page_index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=page_index: self._navigate_to(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # Set dashboard as default
        self.nav_buttons[0].setChecked(True)

        # Spacer
        sidebar_layout.addStretch()

        # Tracking status indicator
        self.tracking_status_label = QLabel("  [ON] Tracking Active")
        self.tracking_status_label.setObjectName("trackingStatus")
        self.tracking_status_label.setFixedHeight(35)
        sidebar_layout.addWidget(self.tracking_status_label)

        # Version label
        version_label = QLabel(f"  v{app_config.version}")
        version_label.setObjectName("versionLabel")
        version_label.setFixedHeight(30)
        sidebar_layout.addWidget(version_label)

        return sidebar

    def _navigate_to(self, page_index: int) -> None:
        """Switch to a specific page."""
        self.content_stack.setCurrentIndex(page_index)

        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == page_index)

        current_widget = self.content_stack.currentWidget()
        if hasattr(current_widget, "refresh_data"):
            current_widget.refresh_data()

        logger.debug(f"Navigated to page {page_index}")

    def _connect_signals(self) -> None:
        """Connect inter-component signals."""
        self.activity_tracker.activity_logged.connect(self._on_activity_logged)
        self.activity_tracker.tracking_status_changed.connect(self._on_tracking_status_changed)

        self.focus_manager.session_started.connect(
            lambda: self.notification_service.notify_focus_session_started(
                self.focus_manager.get_remaining_minutes()
            )
        )
        self.focus_manager.session_ended.connect(self.notification_service.notify_focus_session_ended)

    def _on_activity_logged(self, log_message: str) -> None:
        """Handle new activity log from tracker."""
        if hasattr(self, "activity_log_widget"):
            self.activity_log_widget.append_log(log_message)

    def _on_tracking_status_changed(self, is_tracking: bool) -> None:
        """Update tracking status indicator."""
        if is_tracking:
            self.tracking_status_label.setText("  [ON] Tracking Active")
        else:
            self.tracking_status_label.setText("  [OFF] Tracking Stopped")

    def closeEvent(self, event) -> None:
        """Clean shutdown when window is closed."""
        logger.info("Closing application...")

        if self.activity_tracker.isRunning():
            self.activity_tracker.stop_tracking()
            self.activity_tracker.wait(3000)

        if self.focus_manager.is_active:
            self.focus_manager.end_session()

        self.notification_service.stop_break_reminders()

        event.accept()

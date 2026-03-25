# ui/widgets/settings_widget.py
"""
Settings page — configure app behavior, categories, themes, and preferences.
"""

import os

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config.constants import AppCategory
from config.settings import app_config
from database.connection import DatabasePool
from tracking.activity_tracker import ActivityTracker
from tracking.categorizer import AppCategorizer
from utils.logger import setup_logger

logger = setup_logger("ui.settings")


class SettingsWidget(QWidget):
    """Application settings page with theme toggle."""

    def __init__(self, db_pool: DatabasePool, tracker: ActivityTracker, parent=None):
        super().__init__(parent)
        self.db_pool = db_pool
        self.tracker = tracker
        self.categorizer = AppCategorizer(db_pool)
        self._current_theme = "light"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("⚙️ Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Configure tracking, categories, appearance, and preferences")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        # ──── Appearance Settings ────
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        # Theme toggle
        theme_row = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["☀️  Light Theme", "🌙  Dark Theme"])
        self.theme_combo.setFixedWidth(200)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        appearance_layout.addRow("Theme:", theme_row)

        layout.addWidget(appearance_group)

        # ──── Tracking Settings ────
        tracking_group = QGroupBox("Tracking Settings")
        tracking_layout = QFormLayout(tracking_group)

        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 60)
        self.interval_input.setValue(app_config.tracking_interval)
        self.interval_input.setSuffix(" seconds")
        tracking_layout.addRow("Tracking Interval:", self.interval_input)

        self.retention_input = QSpinBox()
        self.retention_input.setRange(7, 365)
        self.retention_input.setValue(app_config.log_retention_days)
        self.retention_input.setSuffix(" days")
        tracking_layout.addRow("Log Retention:", self.retention_input)

        save_tracking_btn = QPushButton("💾  Save Tracking Settings")
        save_tracking_btn.clicked.connect(self._save_tracking_settings)
        tracking_layout.addRow("", save_tracking_btn)

        layout.addWidget(tracking_group)

        # ──── App Categories Manager ────
        categories_group = QGroupBox("App Categories")
        categories_layout = QVBoxLayout(categories_group)

        # Add new rule row
        add_row = QHBoxLayout()
        self.new_keyword_input = QLineEdit()
        self.new_keyword_input.setPlaceholderText("Keyword (e.g., 'slack')")
        add_row.addWidget(self.new_keyword_input, 2)

        self.new_category_input = QComboBox()
        self.new_category_input.addItems(["productive", "unproductive", "neutral"])
        self.new_category_input.setFixedWidth(150)
        add_row.addWidget(self.new_category_input)

        add_btn = QPushButton("➕  Add Rule")
        add_btn.setObjectName("successButton")
        add_btn.clicked.connect(self._add_category_rule)
        add_row.addWidget(add_btn)
        categories_layout.addLayout(add_row)

        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Keyword", "Category", "Action"])
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.rules_table.setColumnWidth(1, 130)
        self.rules_table.setColumnWidth(2, 80)
        self.rules_table.verticalHeader().setVisible(False)
        self.rules_table.setEditTriggers(QTableWidget.NoEditTriggers)
        categories_layout.addWidget(self.rules_table)

        layout.addWidget(categories_group, 1)

        # ──── Danger Zone ────
        danger_group = QGroupBox("⚠️  Danger Zone")
        danger_layout = QVBoxLayout(danger_group)

        cleanup_row = QHBoxLayout()
        cleanup_label = QLabel("Permanently delete old activity logs beyond retention period")
        cleanup_label.setStyleSheet("color: #8e8ea0;")
        cleanup_row.addWidget(cleanup_label)
        cleanup_row.addStretch()

        cleanup_btn = QPushButton("🗑️  Cleanup Old Logs")
        cleanup_btn.setObjectName("dangerButton")
        cleanup_btn.clicked.connect(self._cleanup_logs)
        cleanup_row.addWidget(cleanup_btn)
        danger_layout.addLayout(cleanup_row)

        layout.addWidget(danger_group)

    def _on_theme_changed(self, index: int) -> None:
        """Switch between light and dark theme."""
        main_window = self.window()  # Get the top-level MainWindow
        styles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")

        if index == 0:
            theme_file = os.path.join(styles_dir, "style.qss")
            self._current_theme = "light"
        else:
            theme_file = os.path.join(styles_dir, "dark_theme.qss")
            self._current_theme = "dark"

        try:
            with open(theme_file, encoding="utf-8") as f:
                main_window.setStyleSheet(f.read())
            logger.info(f"Theme switched to: {self._current_theme}")
        except FileNotFoundError:
            logger.error(f"Theme file not found: {theme_file}")
            QMessageBox.warning(self, "Error", f"Theme file not found: {theme_file}")

    def refresh_data(self):
        """Reload settings data."""
        self._load_category_rules()

    def _save_tracking_settings(self):
        """Save tracking interval and retention settings."""
        new_interval = self.interval_input.value()
        self.tracker.set_interval(new_interval)
        QMessageBox.information(self, "Saved", f"✅ Tracking interval updated to {new_interval} seconds.")
        logger.info(f"Settings updated: interval={new_interval}s")

    def _load_category_rules(self):
        """Load all category rules into the table."""
        rules = self.categorizer.get_all_rules()
        self.rules_table.setRowCount(len(rules))

        for row, (keyword, category) in enumerate(rules.items()):
            self.rules_table.setItem(row, 0, QTableWidgetItem(keyword))

            cat_item = QTableWidgetItem(category)
            color_map = {
                "productive": "#00c897",
                "unproductive": "#ff4757",
                "neutral": "#ffa502",
            }
            cat_item.setForeground(QColor(color_map.get(category, "#8e8ea0")))
            cat_item.setFont(self.rules_table.font())
            self.rules_table.setItem(row, 1, cat_item)

            delete_btn = QPushButton("✕")
            delete_btn.setObjectName("dangerButton")
            delete_btn.setFixedSize(32, 28)
            delete_btn.clicked.connect(lambda checked, k=keyword: self._delete_rule(k))
            self.rules_table.setCellWidget(row, 2, delete_btn)

    def _add_category_rule(self):
        """Add a new categorization rule."""
        keyword = self.new_keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Invalid", "Keyword cannot be empty.")
            return

        category = AppCategory(self.new_category_input.currentText())
        success = self.categorizer.add_rule(keyword, category)

        if success:
            self.new_keyword_input.clear()
            self._load_category_rules()
            QMessageBox.information(self, "Success", f"✅ Rule added: '{keyword}' → {category.value}")
        else:
            QMessageBox.warning(self, "Error", "Failed to add rule.")

    def _delete_rule(self, keyword: str):
        """Delete a categorization rule."""
        self.categorizer.remove_rule(keyword)
        self._load_category_rules()

    def _cleanup_logs(self):
        """Delete old activity logs."""
        days = self.retention_input.value()
        reply = QMessageBox.question(
            self,
            "Confirm Cleanup",
            f"⚠️ This will permanently delete all activity logs older than {days} days.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            from database.repositories.activity_repo import ActivityRepository

            repo = ActivityRepository(self.db_pool)
            success = repo.cleanup_old_logs(days)
            if success:
                QMessageBox.information(self, "Done", f"✅ Logs older than {days} days deleted.")
            else:
                QMessageBox.warning(self, "Error", "Cleanup failed.")

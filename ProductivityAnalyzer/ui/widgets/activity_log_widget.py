# ui/widgets/activity_log_widget.py
"""
Activity log page — shows real-time and historical activity entries.
"""

from datetime import date

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config.constants import AppCategory
from database.connection import DatabasePool
from database.repositories.activity_repo import ActivityRepository
from utils.logger import setup_logger

logger = setup_logger("ui.activity_log")


class ActivityLogWidget(QWidget):
    """Activity log viewer with live feed and historical data."""

    def __init__(self, db_pool: DatabasePool, parent=None):
        super().__init__(parent)
        self.activity_repo = ActivityRepository(db_pool)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("📝 Activity Log")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Real-time tracking feed and historical activity data")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        # ── Live Feed Section ──
        live_label = QLabel("🔴 Live Feed")
        live_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(live_label)

        self.live_log = QTextEdit()
        self.live_log.setObjectName("logArea")
        self.live_log.setReadOnly(True)
        self.live_log.setMaximumHeight(180)
        self.live_log.setPlaceholderText("Activity will appear here as it's tracked...")
        layout.addWidget(self.live_log)

        # ── Filter Bar ──
        filter_row = QHBoxLayout()

        filter_row.addWidget(QLabel("Date:"))
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setFixedWidth(140)
        filter_row.addWidget(self.date_filter)

        filter_row.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "Productive", "Unproductive", "Neutral", "Idle"])
        self.category_filter.setFixedWidth(140)
        filter_row.addWidget(self.category_filter)

        filter_btn = QPushButton("🔍 Filter")
        filter_btn.setFixedWidth(100)
        filter_btn.clicked.connect(self.refresh_data)
        filter_row.addWidget(filter_btn)

        filter_row.addStretch()

        total_label_title = QLabel("Total entries:")
        total_label_title.setStyleSheet("font-weight: bold;")
        filter_row.addWidget(total_label_title)
        self.total_count_label = QLabel("0")
        self.total_count_label.setStyleSheet("color: #0984e3; font-weight: bold; font-size: 14px;")
        filter_row.addWidget(self.total_count_label)

        layout.addLayout(filter_row)

        # ── History Table ──
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Timestamp", "Window Title", "Category", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def refresh_data(self):
        """Reload table data based on filters."""
        try:
            qdate = self.date_filter.date()
            target_date = date(qdate.year(), qdate.month(), qdate.day())
            activities = self.activity_repo.get_activities_by_date(target_date)

            # Apply category filter
            category_text = self.category_filter.currentText()
            if category_text != "All":
                activities = [a for a in activities if a.category.value == category_text.lower()]

            self.table.setRowCount(len(activities))
            for row, activity in enumerate(activities):
                self.table.setItem(row, 0, QTableWidgetItem(str(activity.id or "")))
                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(activity.timestamp.strftime("%H:%M:%S") if activity.timestamp else ""),
                )
                self.table.setItem(row, 2, QTableWidgetItem(activity.window_title[:80]))

                cat_item = QTableWidgetItem(activity.category.value.capitalize())
                cat_colors = {
                    AppCategory.PRODUCTIVE: "#2ecc71",
                    AppCategory.UNPRODUCTIVE: "#e74c3c",
                    AppCategory.NEUTRAL: "#f39c12",
                    AppCategory.IDLE: "#95a5a6",
                }
                from PyQt5.QtGui import QColor

                cat_item.setForeground(QColor(cat_colors.get(activity.category, "#333")))
                self.table.setItem(row, 3, cat_item)

                duration_str = f"{activity.duration_seconds}s" if activity.duration_seconds else "—"
                self.table.setItem(row, 4, QTableWidgetItem(duration_str))

            self.total_count_label.setText(str(len(activities)))
            logger.debug(f"Activity log refreshed: {len(activities)} entries for {target_date}")

        except Exception as e:
            logger.error(f"Error refreshing activity log: {e}", exc_info=True)

    def append_log(self, message: str):
        """Append a message to the live feed."""
        self.live_log.append(message)
        # Auto-scroll to bottom
        scrollbar = self.live_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

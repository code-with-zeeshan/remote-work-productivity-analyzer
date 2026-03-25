# ui/widgets/dashboard_widget.py
"""
Dashboard page — shows overview stats, charts, and suggestions.
"""

from datetime import date

from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database.connection import DatabasePool
from reporting.charts.productivity_pie import ProductivityPieChart
from reporting.charts.trend_line import ProductivityTrendChart
from reporting.report_generator import ReportGenerator
from services.suggestion_engine import SuggestionEngine
from utils.logger import setup_logger
from utils.validators import format_score_color, format_seconds

logger = setup_logger("ui.dashboard")


class StatCard(QFrame):
    """Reusable stat card widget."""

    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#2d3436", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet("color: #636e72; font-size: 11px;")
            layout.addWidget(sub_label)

    def update_value(self, value: str, color: str = None):
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color};")


class DashboardWidget(QWidget):
    """Main dashboard showing overview of productivity."""

    def __init__(
        self,
        db_pool: DatabasePool,
        report_gen: ReportGenerator,
        suggestion_engine: SuggestionEngine,
        parent=None,
    ):
        super().__init__(parent)
        self.db_pool = db_pool
        self.report_gen = report_gen
        self.suggestion_engine = suggestion_engine
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(15)

        # Page header
        title = QLabel("📊 Dashboard")
        title.setObjectName("pageTitle")
        self.main_layout.addWidget(title)

        subtitle = QLabel(f"Overview for {date.today().strftime('%A, %B %d, %Y')}")
        subtitle.setObjectName("pageSubtitle")
        self.main_layout.addWidget(subtitle)

        # ── Stat Cards Row ──
        stats_row = QHBoxLayout()
        stats_row.setSpacing(15)

        self.score_card = StatCard("PRODUCTIVITY SCORE", "—", "Loading...")
        self.productive_card = StatCard("PRODUCTIVE TIME", "—", "")
        self.unproductive_card = StatCard("UNPRODUCTIVE TIME", "—", "")
        self.total_card = StatCard("TOTAL TRACKED", "—", "")

        stats_row.addWidget(self.score_card)
        stats_row.addWidget(self.productive_card)
        stats_row.addWidget(self.unproductive_card)
        stats_row.addWidget(self.total_card)
        self.main_layout.addLayout(stats_row)

        # ── Charts Row ──
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)

        self.pie_container = QFrame()
        self.pie_container.setObjectName("card")
        self.pie_layout = QVBoxLayout(self.pie_container)
        charts_row.addWidget(self.pie_container, 1)

        self.trend_container = QFrame()
        self.trend_container.setObjectName("card")
        self.trend_layout = QVBoxLayout(self.trend_container)
        charts_row.addWidget(self.trend_container, 2)

        self.main_layout.addLayout(charts_row)

        # ── Suggestions Section ──
        suggestions_label = QLabel("💡 Suggestions")
        suggestions_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-top: 5px;")
        self.main_layout.addWidget(suggestions_label)

        self.suggestions_container = QVBoxLayout()
        self.main_layout.addLayout(self.suggestions_container)

        self.main_layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def refresh_data(self):
        """Reload all dashboard data."""
        try:
            # Get daily summary
            summary = self.report_gen.get_daily_summary()

            # Update stat cards
            score_color = format_score_color(summary.score)
            self.score_card.update_value(f"{summary.score}", score_color)
            self.productive_card.update_value(format_seconds(summary.productive_seconds), "#2ecc71")
            self.unproductive_card.update_value(format_seconds(summary.unproductive_seconds), "#e74c3c")
            self.total_card.update_value(format_seconds(summary.total_seconds), "#0984e3")

            # Update pie chart
            self._clear_layout(self.pie_layout)
            pie_chart = ProductivityPieChart(summary, parent=self.pie_container, width=4, height=3.5)
            self.pie_layout.addWidget(pie_chart)

            # Update trend chart
            self._clear_layout(self.trend_layout)
            weekly = self.report_gen.get_weekly_summaries()
            trend_chart = ProductivityTrendChart(weekly, parent=self.trend_container, width=6, height=3.5)
            self.trend_layout.addWidget(trend_chart)

            # Update suggestions
            self._update_suggestions()

        except Exception as e:
            logger.error(f"Dashboard refresh error: {e}", exc_info=True)

    def _update_suggestions(self):
        """Refresh the suggestions list."""
        self._clear_layout(self.suggestions_container)

        suggestions = self.suggestion_engine.get_suggestions()
        for suggestion in suggestions[:5]:  # Show top 5
            card = QFrame()
            card.setObjectName("suggestionCard")

            # Set priority-specific style
            priority_styles = {
                "critical": "suggestionCritical",
                "warning": "suggestionWarning",
                "positive": "suggestionPositive",
                "info": "suggestionInfo",
            }
            style_name = priority_styles.get(suggestion.priority, "suggestionInfo")
            card.setProperty("class", style_name)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #ffffff;
                    border: 1px solid #dfe6e9;
                    border-radius: 8px;
                    border-left: 4px solid {'#d63031' if suggestion.priority == 'critical' else '#fdcb6e' if suggestion.priority == 'warning' else '#00b894' if suggestion.priority == 'positive' else '#0984e3'};
                    padding: 10px;
                    margin: 2px 0;
                }}
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)

            header = QLabel(f"{suggestion.icon} {suggestion.title}")
            header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d3436;")
            card_layout.addWidget(header)

            desc = QLabel(suggestion.description)
            desc.setStyleSheet("font-size: 12px; color: #636e72;")
            desc.setWordWrap(True)
            card_layout.addWidget(desc)

            self.suggestions_container.addWidget(card)

    @staticmethod
    def _clear_layout(layout):
        """Remove all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

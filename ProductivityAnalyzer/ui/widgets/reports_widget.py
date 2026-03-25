# ui/widgets/reports_widget.py
"""
Reports page - view charts and export reports.
"""

from datetime import date

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.connection import DatabasePool
from database.repositories.activity_repo import ActivityRepository
from reporting.charts.activity_chart import ActivityBarChart
from reporting.charts.productivity_pie import ProductivityPieChart
from reporting.charts.trend_line import ProductivityTrendChart
from reporting.exporters.csv_exporter import CSVExporter
from reporting.exporters.pdf_exporter import PDFExporter
from reporting.report_generator import ReportGenerator
from utils.logger import setup_logger

logger = setup_logger("ui.reports")


class ReportsWidget(QWidget):
    """Reports and data visualization page."""

    def __init__(self, db_pool: DatabasePool, parent=None) -> None:
        super().__init__(parent)
        self.db_pool = db_pool
        self.report_gen = ReportGenerator(db_pool)
        self.activity_repo = ActivityRepository(db_pool)
        self.csv_exporter = CSVExporter(db_pool)
        self.pdf_exporter = PDFExporter(db_pool)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("Reports & Analytics")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Visualize your productivity data and export reports")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        # Controls Row
        controls = QHBoxLayout()

        controls.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedWidth(140)
        controls.addWidget(self.date_input)

        controls.addWidget(QLabel("Chart:"))
        self.chart_selector = QComboBox()
        self.chart_selector.addItems(
            [
                "Productivity Pie",
                "Weekly Trend",
                "Monthly Trend",
                "Quarterly Trend",
                "Daily Activity Bars",
            ]
        )
        self.chart_selector.setFixedWidth(200)
        controls.addWidget(self.chart_selector)

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.refresh_data)
        controls.addWidget(generate_btn)

        controls.addStretch()

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.setObjectName("secondaryButton")
        export_csv_btn.clicked.connect(self._export_csv)
        controls.addWidget(export_csv_btn)

        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.setObjectName("secondaryButton")
        export_pdf_btn.clicked.connect(self._export_pdf)
        controls.addWidget(export_pdf_btn)

        layout.addLayout(controls)

        # Chart Container
        self.chart_container = QFrame()
        self.chart_container.setObjectName("card")
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(10, 10, 10, 10)

        placeholder = QLabel("Select a chart type and click Generate")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #636e72; font-size: 16px; padding: 50px;")
        self.chart_layout.addWidget(placeholder)

        layout.addWidget(self.chart_container, 1)

    def refresh_data(self) -> None:
        """Generate and display the selected chart."""
        try:
            self._clear_chart()

            chart_type = self.chart_selector.currentText()
            qdate = self.date_input.date()
            target_date = date(qdate.year(), qdate.month(), qdate.day())

            if chart_type == "Productivity Pie":
                summary = self.report_gen.get_daily_summary(target_date)
                chart = ProductivityPieChart(summary, parent=self.chart_container, width=6, height=5)
                self.chart_layout.addWidget(chart)

            elif chart_type == "Weekly Trend":
                summaries = self.report_gen.get_weekly_summaries()
                chart = ProductivityTrendChart(summaries, parent=self.chart_container, width=9, height=5)
                self.chart_layout.addWidget(chart)

            elif chart_type == "Monthly Trend":
                summaries = self.report_gen.get_monthly_summaries()
                chart = ProductivityTrendChart(summaries, parent=self.chart_container, width=9, height=5)
                self.chart_layout.addWidget(chart)

            elif chart_type == "Quarterly Trend":
                summaries = self.report_gen.get_quarterly_summaries()
                chart = ProductivityTrendChart(summaries, parent=self.chart_container, width=9, height=5)
                self.chart_layout.addWidget(chart)

            elif chart_type == "Daily Activity Bars":
                daily_counts = self.activity_repo.get_daily_counts(days=7)
                chart = ActivityBarChart(daily_counts, parent=self.chart_container, width=9, height=5)
                self.chart_layout.addWidget(chart)

            logger.info(f"Generated chart: {chart_type}")

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Could not generate report: {e}")

    def _export_csv(self) -> None:
        try:
            filepath = self.csv_exporter.export_weekly_report()
            QMessageBox.information(self, "Export Complete", f"CSV report saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {e}")

    def _export_pdf(self) -> None:
        try:
            qdate = self.date_input.date()
            target_date = date(qdate.year(), qdate.month(), qdate.day())
            filepath = self.pdf_exporter.export_daily_report(target_date)
            QMessageBox.information(self, "Export Complete", f"PDF report saved to:\n{filepath}")
        except ImportError:
            QMessageBox.warning(self, "Missing Dependency", "Install reportlab: pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export PDF: {e}")

    def _clear_chart(self) -> None:
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

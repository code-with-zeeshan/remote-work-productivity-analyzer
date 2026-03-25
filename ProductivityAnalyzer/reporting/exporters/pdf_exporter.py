# reporting/exporters/pdf_exporter.py
"""
Export productivity reports to PDF format using ReportLab.
"""

import os
from datetime import date

from database.connection import DatabasePool
from reporting.report_generator import ReportGenerator
from utils.logger import setup_logger

logger = setup_logger("reporting.pdf_exporter")

EXPORT_DIR = "exports"


class PDFExporter:
    """Exports productivity reports to PDF."""

    def __init__(self, db_pool: DatabasePool) -> None:
        self.report_gen = ReportGenerator(db_pool)
        os.makedirs(EXPORT_DIR, exist_ok=True)

    def export_daily_report(self, target_date: date | None = None) -> str:
        """Export a daily productivity summary to PDF. Returns file path."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError:
            logger.error("reportlab not installed. Run: pip install reportlab")
            raise ImportError("reportlab is required for PDF export.") from None

        if target_date is None:
            target_date = date.today()

        summary = self.report_gen.get_daily_summary(target_date)
        filename = os.path.join(EXPORT_DIR, f"report_{target_date.isoformat()}.pdf")

        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("ProductivityAnalyzer - Daily Report", styles["Title"]))
        elements.append(Paragraph(f"Date: {target_date.isoformat()}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(
                f"Productivity Score: {summary.score}/100 (Grade: {summary.grade})",
                styles["Heading2"],
            )
        )
        elements.append(Spacer(1, 15))

        data = [
            ["Category", "Time (minutes)", "Percentage"],
            [
                "Productive",
                f"{summary.productive_minutes:.1f}",
                self._pct(summary.productive_seconds, summary.total_seconds),
            ],
            [
                "Unproductive",
                f"{summary.unproductive_minutes:.1f}",
                self._pct(summary.unproductive_seconds, summary.total_seconds),
            ],
            [
                "Neutral",
                f"{summary.neutral_seconds / 60:.1f}",
                self._pct(summary.neutral_seconds, summary.total_seconds),
            ],
            [
                "Idle",
                f"{summary.idle_seconds / 60:.1f}",
                self._pct(summary.idle_seconds, summary.total_seconds),
            ],
            ["Total", f"{summary.total_seconds / 60:.1f}", "100%"],
        ]

        table = Table(data, colWidths=[150, 120, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d2d2d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"Total tracked entries: {summary.total_entries}", styles["Normal"]))

        doc.build(elements)
        logger.info(f"PDF report exported: {filename}")
        return filename

    @staticmethod
    def _pct(part: int, total: int) -> str:
        if total == 0:
            return "0%"
        return f"{(part / total) * 100:.1f}%"

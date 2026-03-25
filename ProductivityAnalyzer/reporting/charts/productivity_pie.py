# reporting/charts/productivity_pie.py
"""
Pie chart showing time distribution across categories.
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from config.constants import CHART_COLORS, AppCategory
from database.models import DailySummary
from utils.logger import setup_logger

logger = setup_logger("charts.pie")


class ProductivityPieChart(FigureCanvas):
    """Matplotlib pie chart showing productive vs unproductive time."""

    def __init__(self, summary: DailySummary, parent=None, width: int = 5, height: int = 5) -> None:
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.fig.patch.set_facecolor("#f4f4f9")
        super().__init__(self.fig)
        self.setParent(parent)
        self._plot(summary)

    def _plot(self, summary: DailySummary) -> None:
        ax = self.fig.add_subplot(111)

        if summary.total_seconds == 0:
            ax.text(
                0.5,
                0.5,
                "No data yet",
                ha="center",
                va="center",
                fontsize=14,
                color="#999",
            )
            ax.set_axis_off()
            return

        labels = []
        sizes = []
        colors = []

        data = [
            ("Productive", summary.productive_seconds, CHART_COLORS[AppCategory.PRODUCTIVE]),
            ("Unproductive", summary.unproductive_seconds, CHART_COLORS[AppCategory.UNPRODUCTIVE]),
            ("Neutral", summary.neutral_seconds, CHART_COLORS[AppCategory.NEUTRAL]),
            ("Idle", summary.idle_seconds, CHART_COLORS[AppCategory.IDLE]),
        ]

        for label, seconds, color in data:
            if seconds > 0:
                labels.append(f"{label}\n({seconds // 60}m)")
                sizes.append(seconds)
                colors.append(color)

        if not sizes:
            ax.text(
                0.5,
                0.5,
                "No data yet",
                ha="center",
                va="center",
                fontsize=14,
            )
            ax.set_axis_off()
            return

        wedges_and_texts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            textprops={"fontsize": 9},
        )

        # pie() returns (patches, texts) or (patches, texts, autotexts) depending on autopct
        if len(wedges_and_texts) >= 3:
            autotexts = wedges_and_texts[2]
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_fontweight("bold")

        ax.set_title(
            f"Time Distribution - Score: {summary.score}/100 ({summary.grade})",
            fontsize=12,
            fontweight="bold",
            pad=15,
        )
        self.fig.tight_layout()

# reporting/charts/trend_line.py
"""
Line chart showing productivity score trends over time.
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database.models import DailySummary
from utils.logger import setup_logger

logger = setup_logger("charts.trend")


class ProductivityTrendChart(FigureCanvas):
    """Line chart showing productivity score trend over multiple days."""

    def __init__(self, summaries: list[DailySummary], parent=None, width=8, height=4):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.fig.patch.set_facecolor("#f4f4f9")
        super().__init__(self.fig)
        self.setParent(parent)
        self._plot(summaries)

    def _plot(self, summaries: list[DailySummary]):
        ax = self.fig.add_subplot(111)

        if not summaries:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14, color="#999")
            ax.set_axis_off()
            return

        dates = [s.date.strftime("%m/%d") for s in summaries]
        scores = [s.score for s in summaries]
        productive = [s.productive_minutes for s in summaries]
        unproductive = [s.unproductive_minutes for s in summaries]

        # Score line
        line1 = ax.plot(dates, scores, "o-", color="#2ecc71", linewidth=2, markersize=6, label="Score")

        # Fill area
        ax.fill_between(dates, scores, alpha=0.1, color="#2ecc71")

        # Second Y-axis for minutes
        ax2 = ax.twinx()
        ax2.bar(
            [i - 0.15 for i in range(len(dates))],
            productive,
            width=0.3,
            alpha=0.4,
            color="#2ecc71",
            label="Productive (min)",
        )
        ax2.bar(
            [i + 0.15 for i in range(len(dates))],
            unproductive,
            width=0.3,
            alpha=0.4,
            color="#e74c3c",
            label="Unproductive (min)",
        )
        ax2.set_ylabel("Minutes", fontsize=10)

        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Score", fontsize=10)
        ax.set_title("Productivity Trend (Last 7 Days)", fontsize=13, fontweight="bold")
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.3)

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")

        self.fig.tight_layout()

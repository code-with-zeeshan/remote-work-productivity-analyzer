# reporting/charts/activity_chart.py
"""
Bar chart showing activity counts per day.
"""

from datetime import date

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from config.constants import CHART_COLORS, AppCategory
from utils.logger import setup_logger

logger = setup_logger("charts.activity")


class ActivityBarChart(FigureCanvas):
    """Matplotlib bar chart embedded in a Qt widget showing daily activity."""

    def __init__(self, daily_counts: list, parent=None, width=8, height=4):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.fig.patch.set_facecolor("#f4f4f9")
        super().__init__(self.fig)
        self.setParent(parent)
        self._plot(daily_counts)

    def _plot(self, daily_counts: list):
        """
        daily_counts: list of dicts with keys: date, category, count
        """
        ax = self.fig.add_subplot(111)

        if not daily_counts:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14, color="#999")
            ax.set_axis_off()
            return

        # Organize data by date and category
        dates = sorted(set(d["date"] for d in daily_counts))
        categories = [AppCategory.PRODUCTIVE, AppCategory.UNPRODUCTIVE, AppCategory.NEUTRAL, AppCategory.IDLE]

        date_labels = [d.strftime("%m/%d") if isinstance(d, date) else str(d) for d in dates]
        x_positions = range(len(dates))
        bar_width = 0.2

        for i, cat in enumerate(categories):
            counts = []
            for d in dates:
                val = next(
                    (
                        item["count"]
                        for item in daily_counts
                        if item["date"] == d and item["category"] == cat.value
                    ),
                    0,
                )
                counts.append(val)
            offset = (i - 1.5) * bar_width
            bars = ax.bar(
                [x + offset for x in x_positions],
                counts,
                bar_width,
                label=cat.value.capitalize(),
                color=CHART_COLORS[cat].lstrip("#"),
                alpha=0.85,
            )

        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Activity Count", fontsize=10)
        ax.set_title("Daily Activity Breakdown", fontsize=13, fontweight="bold")
        ax.set_xticks(list(x_positions))
        ax.set_xticklabels(date_labels, rotation=45, ha="right")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
        self.fig.tight_layout()

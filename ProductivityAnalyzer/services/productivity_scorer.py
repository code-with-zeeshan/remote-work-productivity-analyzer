# services/productivity_scorer.py
"""
Calculates productivity scores from activity data.
"""

from datetime import date

from config.constants import AppCategory
from database.connection import DatabasePool
from database.models import DailySummary
from database.repositories.activity_repo import ActivityRepository
from utils.logger import setup_logger

logger = setup_logger("services.scorer")


class ProductivityScorer:
    """Computes productivity scores based on activity categorization."""

    def __init__(self, db_pool: DatabasePool) -> None:
        self.activity_repo = ActivityRepository(db_pool)

    def calculate_daily_score(self, target_date: date | None = None) -> DailySummary:
        """Calculate a productivity score for a given date."""
        if target_date is None:
            target_date = date.today()

        summary_data = self.activity_repo.get_productivity_summary(target_date, target_date)

        productive = summary_data.get(AppCategory.PRODUCTIVE.value, {}).get("total_seconds", 0)
        unproductive = summary_data.get(AppCategory.UNPRODUCTIVE.value, {}).get("total_seconds", 0)
        neutral = summary_data.get(AppCategory.NEUTRAL.value, {}).get("total_seconds", 0)
        idle = summary_data.get(AppCategory.IDLE.value, {}).get("total_seconds", 0)
        total = productive + unproductive + neutral + idle
        total_entries = sum(d.get("count", 0) for d in summary_data.values())

        if total > 0:
            score = min(100, max(0, (productive * 1.5 - unproductive + neutral * 0.3) / total * 100))
        else:
            score = 0.0

        return DailySummary(
            date=target_date,
            productive_seconds=productive,
            unproductive_seconds=unproductive,
            neutral_seconds=neutral,
            idle_seconds=idle,
            total_entries=total_entries,
            score=round(score, 1),
        )

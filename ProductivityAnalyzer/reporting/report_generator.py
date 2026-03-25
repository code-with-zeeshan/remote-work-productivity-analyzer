# reporting/report_generator.py
"""
Central report generation coordinator.
"""

from datetime import date, timedelta

from config.constants import AppCategory
from database.connection import DatabasePool
from database.models import DailySummary
from database.repositories.activity_repo import ActivityRepository
from utils.logger import setup_logger

logger = setup_logger("reporting.generator")


class ReportGenerator:
    """Generates productivity reports and summaries."""

    def __init__(self, db_pool: DatabasePool) -> None:
        self.db_pool = db_pool
        self.activity_repo = ActivityRepository(db_pool)

    def get_daily_summary(self, target_date: date | None = None) -> DailySummary:
        """Generate a summary for a specific date."""
        if target_date is None:
            target_date = date.today()

        summary_data = self.activity_repo.get_productivity_summary(target_date, target_date)

        productive = summary_data.get(AppCategory.PRODUCTIVE.value, {})
        unproductive = summary_data.get(AppCategory.UNPRODUCTIVE.value, {})
        neutral = summary_data.get(AppCategory.NEUTRAL.value, {})
        idle = summary_data.get(AppCategory.IDLE.value, {})

        prod_seconds = productive.get("total_seconds", 0)
        unprod_seconds = unproductive.get("total_seconds", 0)
        neutral_seconds = neutral.get("total_seconds", 0)
        idle_seconds = idle.get("total_seconds", 0)
        total_entries = sum(d.get("count", 0) for d in summary_data.values())
        total = prod_seconds + unprod_seconds + neutral_seconds + idle_seconds

        if total > 0:
            score = min(
                100,
                max(
                    0,
                    (prod_seconds * 1.5 - unprod_seconds + neutral_seconds * 0.3) / total * 100,
                ),
            )
        else:
            score = 0.0

        return DailySummary(
            date=target_date,
            productive_seconds=prod_seconds,
            unproductive_seconds=unprod_seconds,
            neutral_seconds=neutral_seconds,
            idle_seconds=idle_seconds,
            total_entries=total_entries,
            score=round(score, 1),
        )

    def get_weekly_summaries(self) -> list[DailySummary]:
        """Get daily summaries for the past 7 days."""
        today = date.today()
        summaries: list[DailySummary] = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            summaries.append(self.get_daily_summary(day))
        return summaries

    def get_monthly_summaries(self) -> list[DailySummary]:
        """Get daily summaries for the past 30 days."""
        today = date.today()
        summaries: list[DailySummary] = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            summaries.append(self.get_daily_summary(day))
        return summaries

    def get_quarterly_summaries(self) -> list[DailySummary]:
        """Get weekly aggregated summaries for the past 90 days (12-13 weeks)."""
        today = date.today()
        summaries: list[DailySummary] = []
        for week in range(12, -1, -1):
            week_start = today - timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            if week_end > today:
                week_end = today

            summary_data = self.activity_repo.get_productivity_summary(week_start, week_end)

            productive = summary_data.get(AppCategory.PRODUCTIVE.value, {})
            unproductive = summary_data.get(AppCategory.UNPRODUCTIVE.value, {})
            neutral_d = summary_data.get(AppCategory.NEUTRAL.value, {})
            idle_d = summary_data.get(AppCategory.IDLE.value, {})

            prod_s = productive.get("total_seconds", 0)
            unprod_s = unproductive.get("total_seconds", 0)
            neutral_s = neutral_d.get("total_seconds", 0)
            idle_s = idle_d.get("total_seconds", 0)
            total = prod_s + unprod_s + neutral_s + idle_s

            score = 0.0
            if total > 0:
                score = min(
                    100,
                    max(0, (prod_s * 1.5 - unprod_s + neutral_s * 0.3) / total * 100),
                )

            summaries.append(
                DailySummary(
                    date=week_start,
                    productive_seconds=prod_s,
                    unproductive_seconds=unprod_s,
                    neutral_seconds=neutral_s,
                    idle_seconds=idle_s,
                    total_entries=sum(d.get("count", 0) for d in summary_data.values()),
                    score=round(score, 1),
                )
            )
        return summaries

    def get_top_apps_today(self, limit: int = 10) -> list:
        """Get top apps used today."""
        return self.activity_repo.get_top_apps(date.today(), limit=limit)

    def save_daily_summary(self, summary: DailySummary) -> bool:
        """Persist a daily summary to the daily_summary table."""
        query = """
            INSERT INTO daily_summary
                (summary_date, productive_seconds, unproductive_seconds, neutral_seconds,
                 idle_seconds, total_entries, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (summary_date) DO UPDATE SET
                productive_seconds = EXCLUDED.productive_seconds,
                unproductive_seconds = EXCLUDED.unproductive_seconds,
                neutral_seconds = EXCLUDED.neutral_seconds,
                idle_seconds = EXCLUDED.idle_seconds,
                total_entries = EXCLUDED.total_entries,
                score = EXCLUDED.score
        """
        return self.db_pool.execute_query(
            query,
            (
                summary.date,
                summary.productive_seconds,
                summary.unproductive_seconds,
                summary.neutral_seconds,
                summary.idle_seconds,
                summary.total_entries,
                summary.score,
            ),
        )

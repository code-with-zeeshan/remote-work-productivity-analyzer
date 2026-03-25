# reporting/exporters/csv_exporter.py
"""
Export activity data and reports to CSV format.
"""

import csv
import os
from datetime import date, timedelta

from database.connection import DatabasePool
from database.models import ActivityLog
from database.repositories.activity_repo import ActivityRepository
from utils.logger import setup_logger

logger = setup_logger("reporting.csv_exporter")

EXPORT_DIR = "exports"


class CSVExporter:
    """Exports data to CSV files."""

    def __init__(self, db_pool: DatabasePool) -> None:
        self.activity_repo = ActivityRepository(db_pool)
        os.makedirs(EXPORT_DIR, exist_ok=True)

    def export_daily_activity(self, target_date: date | None = None) -> str:
        """Export a single day's activity to CSV. Returns the file path."""
        if target_date is None:
            target_date = date.today()

        activities = self.activity_repo.get_activities_by_date(target_date)
        filename = os.path.join(EXPORT_DIR, f"activity_{target_date.isoformat()}.csv")

        return self._write_activities(activities, filename)

    def export_date_range(self, start_date: date, end_date: date) -> str:
        """Export activities within a date range to CSV."""
        activities = self.activity_repo.get_activities_date_range(start_date, end_date)
        filename = os.path.join(
            EXPORT_DIR, f"activity_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
        )
        return self._write_activities(activities, filename)

    def export_weekly_report(self) -> str:
        """Export last 7 days of activity."""
        today = date.today()
        start = today - timedelta(days=6)
        return self.export_date_range(start, today)

    def _write_activities(self, activities: list[ActivityLog], filepath: str) -> str:
        """Write activity list to a CSV file."""
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Timestamp", "Window Title", "Category", "Duration (seconds)"])

                for activity in activities:
                    writer.writerow(
                        [
                            activity.id,
                            activity.timestamp.strftime("%Y-%m-%d %H:%M:%S") if activity.timestamp else "",
                            activity.window_title,
                            activity.category.value,
                            activity.duration_seconds,
                        ]
                    )

            logger.info(f"CSV exported: {filepath} ({len(activities)} rows)")
            return filepath

        except Exception as e:
            logger.error(f"CSV export error: {e}")
            raise

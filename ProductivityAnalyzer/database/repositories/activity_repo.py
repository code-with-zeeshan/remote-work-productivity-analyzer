# database/repositories/activity_repo.py
"""
Repository for activity_log table operations.
"""

from datetime import date

from database.connection import DatabasePool
from database.models import ActivityLog
from utils.logger import setup_logger

logger = setup_logger("repo.activity")


class ActivityRepository:
    def __init__(self, db_pool: DatabasePool):
        self.db = db_pool

    def log_activity(self, activity: ActivityLog) -> bool:
        """Insert a new activity log entry."""
        query = """
            INSERT INTO activity_log (timestamp, window_title, category, duration_seconds)
            VALUES (%s, %s, %s, %s)
        """
        params = (
            activity.timestamp,
            activity.window_title,
            activity.category.value,
            activity.duration_seconds,
        )
        success = self.db.execute_query(query, params)
        if success:
            logger.debug(f"Logged: [{activity.category.value}] {activity.window_title[:50]}")
        return success

    def get_activities_by_date(self, target_date: date) -> list[ActivityLog]:
        """Get all activities for a specific date."""
        query = """
            SELECT id, timestamp, window_title, category, duration_seconds
            FROM activity_log
            WHERE DATE(timestamp) = %s
            ORDER BY timestamp DESC
        """
        rows = self.db.fetch_all(query, (target_date,))
        return [ActivityLog.from_db_row(row) for row in rows]

    def get_activities_date_range(self, start_date: date, end_date: date) -> list[ActivityLog]:
        """Get activities within a date range."""
        query = """
            SELECT id, timestamp, window_title, category, duration_seconds
            FROM activity_log
            WHERE DATE(timestamp) BETWEEN %s AND %s
            ORDER BY timestamp DESC
        """
        rows = self.db.fetch_all(query, (start_date, end_date))
        return [ActivityLog.from_db_row(row) for row in rows]

    def get_recent_activities(self, limit: int = 50) -> list[ActivityLog]:
        """Get the most recent activities."""
        query = """
            SELECT id, timestamp, window_title, category, duration_seconds
            FROM activity_log
            ORDER BY timestamp DESC
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (limit,))
        return [ActivityLog.from_db_row(row) for row in rows]

    def get_productivity_summary(self, start_date: date, end_date: date) -> dict:
        """Get aggregated time per category for a date range."""
        query = """
            SELECT category, COUNT(*) as entry_count, COALESCE(SUM(duration_seconds), 0) as total_seconds
            FROM activity_log
            WHERE DATE(timestamp) BETWEEN %s AND %s
            GROUP BY category
        """
        rows = self.db.fetch_all(query, (start_date, end_date))
        return {row[0]: {"count": row[1], "total_seconds": row[2]} for row in rows}

    def get_top_apps(self, target_date: date, category: str | None = None, limit: int = 10) -> list[dict]:
        """Get top applications by time spent."""
        if category:
            query = """
                SELECT window_title, COUNT(*) as count, COALESCE(SUM(duration_seconds), 0) as total
                FROM activity_log
                WHERE DATE(timestamp) = %s AND category = %s
                GROUP BY window_title
                ORDER BY total DESC
                LIMIT %s
            """
            rows = self.db.fetch_all(query, (target_date, category, limit))
        else:
            query = """
                SELECT window_title, COUNT(*) as count, COALESCE(SUM(duration_seconds), 0) as total
                FROM activity_log
                WHERE DATE(timestamp) = %s
                GROUP BY window_title
                ORDER BY total DESC
                LIMIT %s
            """
            rows = self.db.fetch_all(query, (target_date, limit))

        return [{"window_title": r[0], "count": r[1], "total_seconds": r[2]} for r in rows]

    def get_daily_counts(self, days: int = 7) -> list[dict]:
        """Get activity counts per day for the last N days."""
        query = """
            SELECT DATE(timestamp) as day, category, COUNT(*) as count
            FROM activity_log
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp), category
            ORDER BY day
        """
        rows = self.db.fetch_all(query, (days,))
        return [{"date": r[0], "category": r[1], "count": r[2]} for r in rows]

    def cleanup_old_logs(self, retention_days: int = 90) -> bool:
        """Delete logs older than retention period."""
        query = "DELETE FROM activity_log WHERE timestamp < NOW() - INTERVAL '%s days'"
        success = self.db.execute_query(query, (retention_days,))
        if success:
            logger.info(f"Cleaned up logs older than {retention_days} days")
        return success

    def get_total_count(self) -> int:
        """Get total number of activity log entries."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM activity_log")
        return result[0] if result else 0

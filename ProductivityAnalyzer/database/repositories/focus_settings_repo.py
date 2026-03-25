# database/repositories/focus_settings_repo.py
"""
Repository for focus_settings table operations.
"""

from database.connection import DatabasePool
from database.models import FocusSettings
from utils.logger import setup_logger

logger = setup_logger("repo.focus_settings")


class FocusSettingsRepository:
    def __init__(self, db_pool: DatabasePool):
        self.db = db_pool

    def save_settings(self, settings: FocusSettings) -> int | None:
        """Save or update focus settings. Returns the ID."""
        if settings.id:
            return self._update_settings(settings)
        return self._insert_settings(settings)

    def _insert_settings(self, settings: FocusSettings) -> int | None:
        """Insert new focus settings."""
        query = """
            INSERT INTO focus_settings (start_time, end_time, blocked_apps, blocked_websites, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        blocked_apps_str = ",".join(settings.blocked_apps)
        blocked_websites_str = ",".join(settings.blocked_websites)
        result = self.db.execute_query_returning(
            query,
            (
                settings.start_time,
                settings.end_time,
                blocked_apps_str,
                blocked_websites_str,
                settings.is_active,
            ),
        )
        if result:
            logger.info(f"Focus settings saved with id={result}")
        return result

    def _update_settings(self, settings: FocusSettings) -> int | None:
        """Update existing focus settings."""
        query = """
            UPDATE focus_settings
            SET start_time = %s, end_time = %s, blocked_apps = %s,
                blocked_websites = %s, is_active = %s
            WHERE id = %s
        """
        blocked_apps_str = ",".join(settings.blocked_apps)
        blocked_websites_str = ",".join(settings.blocked_websites)
        self.db.execute_query(
            query,
            (
                settings.start_time,
                settings.end_time,
                blocked_apps_str,
                blocked_websites_str,
                settings.is_active,
                settings.id,
            ),
        )
        return settings.id

    def get_active_settings(self) -> FocusSettings | None:
        """Get the currently active focus settings."""
        query = """
            SELECT id, start_time, end_time, blocked_apps, blocked_websites, is_active, created_at
            FROM focus_settings
            WHERE is_active = TRUE
            ORDER BY id DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query)
        if row:
            return FocusSettings.from_db_row(row)
        return None

    def get_latest_settings(self) -> FocusSettings | None:
        """Get the most recent focus settings regardless of active status."""
        query = """
            SELECT id, start_time, end_time, blocked_apps, blocked_websites, is_active, created_at
            FROM focus_settings
            ORDER BY id DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query)
        if row:
            return FocusSettings.from_db_row(row)
        return None

    def deactivate_all(self) -> bool:
        """Deactivate all focus settings."""
        return self.db.execute_query("UPDATE focus_settings SET is_active = FALSE WHERE is_active = TRUE")

    def get_all_settings(self) -> list[FocusSettings]:
        """Get all focus settings history."""
        query = """
            SELECT id, start_time, end_time, blocked_apps, blocked_websites, is_active, created_at
            FROM focus_settings
            ORDER BY id DESC
        """
        rows = self.db.fetch_all(query)
        return [FocusSettings.from_db_row(row) for row in rows]

# database/migrations/migration_002_soft_deletes.py
"""
Migration 002: Add soft delete support to all tables.
"""

from database.connection import DatabasePool
from utils.logger import setup_logger

logger = setup_logger("migration.002")

MIGRATION_VERSION = 2
MIGRATION_NAME = "soft_deletes"

SQL_STATEMENTS = [
    # Add deleted_at column to activity_log
    """
    ALTER TABLE activity_log
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
    """,
    # Add deleted_at column to goals
    """
    ALTER TABLE goals
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
    """,
    # Add deleted_at column to focus_settings
    """
    ALTER TABLE focus_settings
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
    """,
    # Add deleted_at column to app_categories
    """
    ALTER TABLE app_categories
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL;
    """,
    # Index for efficient soft-delete filtering
    """
    CREATE INDEX IF NOT EXISTS idx_activity_not_deleted
    ON activity_log(deleted_at) WHERE deleted_at IS NULL;
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_goals_not_deleted
    ON goals(deleted_at) WHERE deleted_at IS NULL;
    """,
]


def run_migration(db_pool: DatabasePool):
    """Execute migration if not already applied."""
    logger.info(f"Checking migration {MIGRATION_VERSION}: {MIGRATION_NAME}")

    result = db_pool.fetch_one(
        "SELECT version FROM schema_migrations WHERE version = %s",
        (MIGRATION_VERSION,),
    )
    if result:
        logger.info(f"Migration {MIGRATION_VERSION} already applied, skipping.")
        return

    logger.info(f"Applying migration {MIGRATION_VERSION}: {MIGRATION_NAME}")

    with db_pool.get_connection() as conn, conn.cursor() as cursor:
        for i, sql in enumerate(SQL_STATEMENTS):
            try:
                cursor.execute(sql)
                logger.debug(f"  Statement {i + 1}/{len(SQL_STATEMENTS)} executed")
            except Exception as e:
                logger.warning(f"  Statement {i + 1} skipped: {e}")

        cursor.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
            (MIGRATION_VERSION, MIGRATION_NAME),
        )
        conn.commit()

    logger.info(f"Migration {MIGRATION_VERSION} applied successfully!")

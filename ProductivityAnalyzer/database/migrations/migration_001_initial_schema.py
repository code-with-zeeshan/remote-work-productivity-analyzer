# database/migrations/migration_001_initial_schema.py
"""
Migration 001: Initial Schema for ProductivityAnalyzer v2.0

Creates all tables, indexes, and seed data.
"""

from database.connection import DatabasePool
from utils.logger import setup_logger

logger = setup_logger("migration.001")

MIGRATION_VERSION = 1
MIGRATION_NAME = "initial_schema"

SQL_STATEMENTS = [
    # ──────────────── Migration Tracking Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        applied_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # ──────────────── Activity Log Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS activity_log (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
        window_title TEXT NOT NULL DEFAULT '',
        category VARCHAR(20) NOT NULL DEFAULT 'neutral',
        duration_seconds INTEGER NOT NULL DEFAULT 0
    );
    """,
    # ──────────────── Focus Settings Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS focus_settings (
        id SERIAL PRIMARY KEY,
        start_time TIME,
        end_time TIME,
        blocked_apps TEXT DEFAULT '',
        blocked_websites TEXT DEFAULT '',
        is_active BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # ──────────────── Goals Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS goals (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        target_hours DECIMAL(5,2) NOT NULL DEFAULT 0,
        period VARCHAR(20) NOT NULL DEFAULT 'daily',
        current_progress DECIMAL(5,2) NOT NULL DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # ──────────────── App Categories Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS app_categories (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(255) NOT NULL UNIQUE,
        category VARCHAR(20) NOT NULL DEFAULT 'neutral',
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # ──────────────── Daily Summary Table ────────────────
    """
    CREATE TABLE IF NOT EXISTS daily_summary (
        id SERIAL PRIMARY KEY,
        summary_date DATE NOT NULL UNIQUE,
        productive_seconds INTEGER DEFAULT 0,
        unproductive_seconds INTEGER DEFAULT 0,
        neutral_seconds INTEGER DEFAULT 0,
        idle_seconds INTEGER DEFAULT 0,
        total_entries INTEGER DEFAULT 0,
        score DECIMAL(5,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # ──────────────── Indexes ────────────────
    "CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_activity_category ON activity_log(category);",
    "CREATE INDEX IF NOT EXISTS idx_activity_date ON activity_log(DATE(timestamp));",
    "CREATE INDEX IF NOT EXISTS idx_goals_active ON goals(is_active);",
    "CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_summary(summary_date);",
    "CREATE INDEX IF NOT EXISTS idx_focus_active ON focus_settings(is_active);",
]

SEED_DATA = [
    # Seed default app categories
    """
    INSERT INTO app_categories (keyword, category) VALUES
        ('visual studio code', 'productive'),
        ('vscode', 'productive'),
        ('pycharm', 'productive'),
        ('intellij', 'productive'),
        ('terminal', 'productive'),
        ('github', 'productive'),
        ('stackoverflow', 'productive'),
        ('jupyter', 'productive'),
        ('postman', 'productive'),
        ('notion', 'productive'),
        ('youtube', 'unproductive'),
        ('facebook', 'unproductive'),
        ('instagram', 'unproductive'),
        ('twitter', 'unproductive'),
        ('reddit', 'unproductive'),
        ('netflix', 'unproductive'),
        ('tiktok', 'unproductive'),
        ('chrome', 'neutral'),
        ('firefox', 'neutral'),
        ('outlook', 'neutral'),
        ('slack', 'neutral')
    ON CONFLICT (keyword) DO NOTHING;
    """,
]


def run_migration(db_pool: DatabasePool):
    """Execute migration if not already applied."""
    logger.info(f"Checking migration {MIGRATION_VERSION}: {MIGRATION_NAME}")

    # Check if migration already applied
    try:
        result = db_pool.fetch_one(
            "SELECT version FROM schema_migrations WHERE version = %s",
            (MIGRATION_VERSION,),
        )
        if result:
            logger.info(f"Migration {MIGRATION_VERSION} already applied, skipping.")
            return
    except Exception:
        # Table doesn't exist yet, that's fine — we'll create it
        pass

    # Run migration
    logger.info(f"Applying migration {MIGRATION_VERSION}: {MIGRATION_NAME}")

    with db_pool.get_connection() as conn, conn.cursor() as cursor:
        for i, sql in enumerate(SQL_STATEMENTS):
            try:
                cursor.execute(sql)
                logger.debug(f"  Statement {i + 1}/{len(SQL_STATEMENTS)} executed")
            except Exception as e:
                logger.error(f"  Statement {i + 1} failed: {e}")
                conn.rollback()
                raise

        # Run seed data
        for i, sql in enumerate(SEED_DATA):
            try:
                cursor.execute(sql)
                logger.debug(f"  Seed data {i + 1}/{len(SEED_DATA)} inserted")
            except Exception as e:
                logger.warning(f"  Seed data {i + 1} skipped: {e}")

        # Record migration
        cursor.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
            (MIGRATION_VERSION, MIGRATION_NAME),
        )
        conn.commit()

    logger.info(f"Migration {MIGRATION_VERSION} applied successfully!")

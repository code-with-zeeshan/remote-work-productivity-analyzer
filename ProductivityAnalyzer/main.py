# main.py
"""
ProductivityAnalyzer v2.0 — Entry Point
"""

import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from config.settings import app_config
from database.connection import DatabasePool
from database.migrations.migration_001_initial_schema import run_migration as run_migration_001
from database.migrations.migration_002_soft_deletes import run_migration as run_migration_002
from ui.main_window import MainWindow
from utils.logger import setup_logger

logger = setup_logger("main")

# ── Sentry Error Tracking (optional) ──
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=0.3,
            environment="production" if not app_config.debug else "development",
            release=f"productivity-analyzer@{app_config.version}",
        )
        logger.info("Sentry error tracking initialized")
    except ImportError:
        logger.warning("sentry-sdk not installed, error tracking disabled")


def main():
    """Application entry point."""
    logger.info("=" * 50)
    logger.info("ProductivityAnalyzer v2.0 Starting...")
    logger.info("=" * 50)

    # 1. Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("ProductivityAnalyzer")
    app.setApplicationVersion("2.0.0")

    # Set app icon if exists
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 2. Initialize Database Pool
    db_pool = None
    try:
        db_pool = DatabasePool()
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to connect to database.\n\n" f"Please check your .env configuration.\n\nError: {e}",
        )
        sys.exit(1)

    # 3. Run Migrations
    try:
        run_migration_001(db_pool)
        run_migration_002(db_pool)
        logger.info("Database migrations completed")
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)

    # 4. Create and Show Main Window
    try:
        window = MainWindow(db_pool=db_pool)
        window.show()
        logger.info("Main window displayed")
    except Exception as e:
        logger.critical(f"Failed to create main window: {e}", exc_info=True)
        if db_pool:
            db_pool.close_all()
        sys.exit(1)

    # 5. Run Event Loop
    exit_code = app.exec_()

    # 6. Cleanup
    logger.info("Application shutting down...")
    if db_pool:
        db_pool.close_all()
    logger.info("Goodbye!")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

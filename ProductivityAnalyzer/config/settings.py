# config/settings.py
"""
Centralized configuration loaded from .env file.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env from project root
load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """Database connection settings."""

    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    host: str = os.getenv("DB_HOST", "localhost")
    port: str = os.getenv("DB_PORT", "5432")
    database: str = os.getenv("DB_NAME", "remotework")
    min_connections: int = int(os.getenv("DB_MIN_CONNECTIONS", "1"))
    max_connections: int = int(os.getenv("DB_MAX_CONNECTIONS", "10"))


@dataclass(frozen=True)
class AppConfig:
    """Application-wide settings."""

    tracking_interval: int = int(os.getenv("TRACKING_INTERVAL", "5"))
    log_retention_days: int = int(os.getenv("LOG_RETENTION_DAYS", "90"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    default_focus_duration: int = int(os.getenv("DEFAULT_FOCUS_DURATION_MINUTES", "25"))
    break_reminder_minutes: int = int(os.getenv("BREAK_REMINDER_MINUTES", "45"))
    app_name: str = "ProductivityAnalyzer"
    version: str = "2.0.0"


# Singleton instances
db_config = DatabaseConfig()
app_config = AppConfig()

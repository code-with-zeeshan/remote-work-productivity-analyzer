# tests/conftest.py
"""
Shared test fixtures and configuration for pytest.
"""

from datetime import date, datetime, time
from unittest.mock import MagicMock

import pytest

from config.constants import AppCategory, GoalPeriod
from database.models import ActivityLog, DailySummary, FocusSettings, ProductivityGoal


@pytest.fixture
def mock_db_pool():
    """Create a mock database pool."""
    pool = MagicMock()
    pool.execute_query.return_value = True
    pool.execute_query_returning.return_value = 1
    pool.fetch_one.return_value = None
    pool.fetch_all.return_value = []
    pool.fetch_all_dict.return_value = []
    return pool


@pytest.fixture
def sample_activity():
    """Create a sample ActivityLog."""
    return ActivityLog(
        id=1,
        timestamp=datetime(2026, 3, 24, 10, 30, 0),
        window_title="Visual Studio Code - main.py",
        category=AppCategory.PRODUCTIVE,
        duration_seconds=300,
    )


@pytest.fixture
def sample_activities():
    """Create a list of sample activities."""
    return [
        ActivityLog(
            id=1,
            timestamp=datetime(2026, 3, 24, 9, 0),
            window_title="VS Code",
            category=AppCategory.PRODUCTIVE,
            duration_seconds=1800,
        ),
        ActivityLog(
            id=2,
            timestamp=datetime(2026, 3, 24, 9, 30),
            window_title="YouTube",
            category=AppCategory.UNPRODUCTIVE,
            duration_seconds=600,
        ),
        ActivityLog(
            id=3,
            timestamp=datetime(2026, 3, 24, 10, 0),
            window_title="Chrome",
            category=AppCategory.NEUTRAL,
            duration_seconds=900,
        ),
        ActivityLog(
            id=4,
            timestamp=datetime(2026, 3, 24, 10, 15),
            window_title="No Active Window",
            category=AppCategory.IDLE,
            duration_seconds=300,
        ),
    ]


@pytest.fixture
def sample_focus_settings():
    """Create sample FocusSettings."""
    return FocusSettings(
        id=1,
        start_time=time(9, 0),
        end_time=time(17, 0),
        blocked_apps=["youtube", "facebook"],
        blocked_websites=["youtube.com", "facebook.com"],
        is_active=True,
    )


@pytest.fixture
def sample_goal():
    """Create a sample ProductivityGoal."""
    return ProductivityGoal(
        id=1,
        title="Code for 4 hours",
        target_hours=4.0,
        period=GoalPeriod.DAILY,
        current_progress=2.5,
        is_active=True,
    )


@pytest.fixture
def sample_daily_summary():
    """Create a sample DailySummary."""
    return DailySummary(
        date=date(2026, 3, 24),
        productive_seconds=7200,
        unproductive_seconds=1800,
        neutral_seconds=3600,
        idle_seconds=900,
        total_entries=150,
        score=72.5,
    )

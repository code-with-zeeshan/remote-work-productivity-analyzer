# tests/test_database/test_activity_repo.py
"""Tests for ActivityRepository."""

from datetime import date, datetime
from unittest.mock import MagicMock

from config.constants import AppCategory
from database.repositories.activity_repo import ActivityRepository


class TestActivityRepository:
    def setup_method(self):
        self.mock_pool = MagicMock()
        self.repo = ActivityRepository(self.mock_pool)

    def test_log_activity_success(self, sample_activity):
        self.mock_pool.execute_query.return_value = True
        result = self.repo.log_activity(sample_activity)
        assert result is True
        self.mock_pool.execute_query.assert_called_once()

    def test_log_activity_failure(self, sample_activity):
        self.mock_pool.execute_query.return_value = False
        result = self.repo.log_activity(sample_activity)
        assert result is False

    def test_get_activities_by_date(self):
        self.mock_pool.fetch_all.return_value = [
            (1, datetime(2026, 3, 24, 10, 0), "VS Code", "productive", 300),
        ]
        activities = self.repo.get_activities_by_date(date(2026, 3, 24))
        assert len(activities) == 1
        assert activities[0].window_title == "VS Code"
        assert activities[0].category == AppCategory.PRODUCTIVE

    def test_get_activities_by_date_empty(self):
        self.mock_pool.fetch_all.return_value = []
        activities = self.repo.get_activities_by_date(date(2026, 1, 1))
        assert len(activities) == 0

    def test_get_productivity_summary(self):
        self.mock_pool.fetch_all.return_value = [
            ("productive", 50, 7200),
            ("unproductive", 20, 1800),
        ]
        summary = self.repo.get_productivity_summary(date(2026, 3, 24), date(2026, 3, 24))
        assert "productive" in summary
        assert summary["productive"]["total_seconds"] == 7200

    def test_get_total_count(self):
        self.mock_pool.fetch_one.return_value = (42,)
        count = self.repo.get_total_count()
        assert count == 42

    def test_get_total_count_empty(self):
        self.mock_pool.fetch_one.return_value = None
        count = self.repo.get_total_count()
        assert count == 0

# tests/test_database/test_goals_repo.py
"""Tests for GoalsRepository."""

from datetime import datetime
from unittest.mock import MagicMock

from config.constants import GoalPeriod
from database.repositories.goals_repo import GoalsRepository


class TestGoalsRepository:
    def setup_method(self):
        self.mock_pool = MagicMock()
        self.repo = GoalsRepository(self.mock_pool)

    def test_create_goal(self, sample_goal):
        self.mock_pool.execute_query_returning.return_value = 1
        result = self.repo.create_goal(sample_goal)
        assert result == 1
        self.mock_pool.execute_query_returning.assert_called_once()

    def test_get_active_goals(self):
        self.mock_pool.fetch_all.return_value = [
            (1, "Code 4 hours", 4.0, "daily", 2.5, True, datetime.now()),
        ]
        goals = self.repo.get_active_goals()
        assert len(goals) == 1
        assert goals[0].title == "Code 4 hours"
        assert goals[0].period == GoalPeriod.DAILY

    def test_update_progress(self):
        self.mock_pool.execute_query.return_value = True
        result = self.repo.update_progress(1, 3.5)
        assert result is True

    def test_delete_goal(self):
        self.mock_pool.execute_query.return_value = True
        result = self.repo.delete_goal(1)
        assert result is True

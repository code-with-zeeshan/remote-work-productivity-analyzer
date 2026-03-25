# tests/test_integration/test_full_workflow.py
"""
Integration tests - test real component interactions (with mocked DB).
"""

from datetime import date
from unittest.mock import MagicMock

from config.constants import AppCategory
from database.models import ActivityLog, DailySummary, ProductivityGoal
from reporting.report_generator import ReportGenerator
from services.suggestion_engine import SuggestionEngine
from tracking.categorizer import AppCategorizer


class TestCategorizerToReportingPipeline:
    """Test that categorizer output feeds correctly into reporting."""

    def test_categorized_activity_flows_to_summary(self):
        """Categorizer -> Activity Log -> Report Generator flow."""
        categorizer = AppCategorizer(db_pool=None)

        # Simulate categorizing activities
        activities = [
            ("Visual Studio Code - main.py", 1800),
            ("YouTube - Funny Videos", 600),
            ("Google Chrome - Search", 300),
            ("No Active Window", 120),
        ]

        results = []
        for title, duration in activities:
            category = categorizer.categorize(title)
            results.append(
                ActivityLog(
                    window_title=title,
                    category=category,
                    duration_seconds=duration,
                )
            )

        assert results[0].category == AppCategory.PRODUCTIVE
        assert results[1].category == AppCategory.UNPRODUCTIVE
        assert results[2].category == AppCategory.NEUTRAL
        assert results[3].category == AppCategory.IDLE

    def test_report_generator_produces_valid_summary(self):
        """ReportGenerator returns correct summary from mock data."""
        mock_pool = MagicMock()
        mock_pool.fetch_all.return_value = [
            ("productive", 30, 5400),
            ("unproductive", 10, 1800),
            ("neutral", 5, 900),
            ("idle", 3, 360),
        ]

        gen = ReportGenerator(mock_pool)
        summary = gen.get_daily_summary(date(2026, 3, 25))

        assert summary.productive_seconds == 5400
        assert summary.unproductive_seconds == 1800
        assert summary.score > 0
        assert summary.total_entries == 48
        assert summary.grade in ("A+", "A", "B", "C", "D", "F")


class TestSuggestionEngineIntegration:
    """Test suggestion engine with realistic data."""

    def test_high_distraction_produces_critical_suggestion(self):
        """High unproductive time triggers critical alert."""
        mock_pool = MagicMock()
        mock_pool.fetch_all.return_value = [
            ("productive", 5, 1000),
            ("unproductive", 20, 5000),
            ("neutral", 2, 500),
        ]

        engine = SuggestionEngine(mock_pool)
        suggestions = engine.get_suggestions()

        priorities = [s.priority for s in suggestions]
        assert "critical" in priorities or "warning" in priorities

    def test_great_productivity_produces_positive_suggestion(self):
        """High productive time triggers positive feedback."""
        mock_pool = MagicMock()
        mock_pool.fetch_all.return_value = [
            ("productive", 50, 14400),
            ("unproductive", 2, 300),
            ("neutral", 5, 900),
        ]

        engine = SuggestionEngine(mock_pool)
        suggestions = engine.get_suggestions()

        has_positive = any(s.priority == "positive" for s in suggestions)
        assert has_positive

    def test_empty_data_still_returns_suggestions(self):
        """Engine handles no data gracefully."""
        mock_pool = MagicMock()
        mock_pool.fetch_all.return_value = []

        engine = SuggestionEngine(mock_pool)
        suggestions = engine.get_suggestions()

        assert len(suggestions) >= 1


class TestGoalProgressIntegration:
    """Test goal model calculations."""

    def test_goal_progress_percentage(self):
        goal = ProductivityGoal(
            title="Code 4 hours",
            target_hours=4.0,
            current_progress=3.0,
        )
        assert goal.progress_percentage == 75.0

    def test_goal_complete(self):
        goal = ProductivityGoal(
            title="Code 4 hours",
            target_hours=4.0,
            current_progress=4.5,
        )
        assert goal.progress_percentage == 100.0

    def test_goal_zero_target(self):
        goal = ProductivityGoal(title="Empty", target_hours=0.0)
        assert goal.progress_percentage == 0.0


class TestDailySummaryModel:
    """Test DailySummary calculations."""

    def test_grade_calculation(self):
        assert DailySummary(score=95).grade == "A+"
        assert DailySummary(score=85).grade == "A"
        assert DailySummary(score=75).grade == "B"
        assert DailySummary(score=65).grade == "C"
        assert DailySummary(score=55).grade == "D"
        assert DailySummary(score=30).grade == "F"

    def test_total_seconds(self):
        s = DailySummary(
            productive_seconds=3600,
            unproductive_seconds=1800,
            neutral_seconds=900,
            idle_seconds=300,
        )
        assert s.total_seconds == 6600

    def test_productive_minutes(self):
        s = DailySummary(productive_seconds=5400)
        assert s.productive_minutes == 90.0

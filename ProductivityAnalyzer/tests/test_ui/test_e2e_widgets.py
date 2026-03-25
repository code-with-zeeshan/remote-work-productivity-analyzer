# tests/test_ui/test_e2e_widgets.py
"""
E2E-style widget tests using pytest-qt.
Tests the actual UI components render correctly.
"""

from unittest.mock import MagicMock

import pytest

# Skip all tests if DISPLAY is not available (headless CI)
pytestmark = pytest.mark.skipif(
    True,  # Set to False when running locally with display
    reason="GUI tests require display. Run locally with: pytest tests/test_ui/test_e2e_widgets.py --no-header",
)


class TestDashboardWidget:
    """Test Dashboard widget rendering."""

    def test_dashboard_creates_without_error(self, qtbot):
        from reporting.report_generator import ReportGenerator
        from services.suggestion_engine import SuggestionEngine
        from ui.widgets.dashboard_widget import DashboardWidget

        mock_pool = MagicMock()
        mock_pool.fetch_all.return_value = []
        mock_pool.fetch_one.return_value = None

        report_gen = ReportGenerator(mock_pool)
        suggestion_engine = SuggestionEngine(mock_pool)

        widget = DashboardWidget(
            db_pool=mock_pool,
            report_gen=report_gen,
            suggestion_engine=suggestion_engine,
        )
        qtbot.addWidget(widget)
        assert widget is not None

    def test_dashboard_stat_cards_exist(self, qtbot):
        from ui.widgets.dashboard_widget import StatCard

        card = StatCard("TEST METRIC", "42", "test subtitle", "#00ff00")
        qtbot.addWidget(card)
        assert card.value_label.text() == "42"

        card.update_value("99", "#ff0000")
        assert card.value_label.text() == "99"


class TestGoalsWidget:
    """Test Goals widget rendering."""

    def test_goal_card_displays_correctly(self, qtbot):
        from config.constants import GoalPeriod
        from database.models import ProductivityGoal
        from ui.widgets.goals_widget import GoalCard

        goal = ProductivityGoal(
            id=1,
            title="Code 4 hours",
            target_hours=4.0,
            current_progress=2.5,
            period=GoalPeriod.DAILY,
        )

        card = GoalCard(goal)
        qtbot.addWidget(card)
        assert card is not None

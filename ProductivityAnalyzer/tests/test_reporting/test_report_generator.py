# tests/test_reporting/test_report_generator.py
"""Tests for ReportGenerator."""

from datetime import date
from unittest.mock import MagicMock, patch

from reporting.report_generator import ReportGenerator


class TestReportGenerator:
    def setup_method(self):
        self.mock_pool = MagicMock()
        self.gen = ReportGenerator(self.mock_pool)

    @patch("reporting.report_generator.ActivityRepository")
    def test_get_daily_summary_empty(self, mock_repo_class):
        mock_repo = MagicMock()
        mock_repo.get_productivity_summary.return_value = {}
        self.gen.activity_repo = mock_repo

        summary = self.gen.get_daily_summary(date(2026, 3, 24))
        assert summary.score == 0.0
        assert summary.total_seconds == 0

    @patch("reporting.report_generator.ActivityRepository")
    def test_get_daily_summary_with_data(self, mock_repo_class):
        mock_repo = MagicMock()
        mock_repo.get_productivity_summary.return_value = {
            "productive": {"count": 50, "total_seconds": 7200},
            "unproductive": {"count": 10, "total_seconds": 1800},
        }
        self.gen.activity_repo = mock_repo

        summary = self.gen.get_daily_summary(date(2026, 3, 24))
        assert summary.productive_seconds == 7200
        assert summary.unproductive_seconds == 1800
        assert summary.score > 0

    @patch("reporting.report_generator.ActivityRepository")
    def test_get_weekly_summaries(self, mock_repo_class):
        mock_repo = MagicMock()
        mock_repo.get_productivity_summary.return_value = {}
        self.gen.activity_repo = mock_repo

        summaries = self.gen.get_weekly_summaries()
        assert len(summaries) == 7

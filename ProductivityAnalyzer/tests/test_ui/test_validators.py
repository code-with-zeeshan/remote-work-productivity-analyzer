# tests/test_ui/test_validators.py
"""Tests for validator utilities."""

from datetime import time

from utils.validators import (
    format_score_color,
    format_seconds,
    validate_blocked_list,
    validate_goal_input,
    validate_time_range,
)


class TestValidateTimeRange:
    def test_valid_range(self):
        valid, msg = validate_time_range(time(9, 0), time(17, 0))
        assert valid is True
        assert msg == ""

    def test_invalid_same_time(self):
        valid, msg = validate_time_range(time(9, 0), time(9, 0))
        assert valid is False

    def test_invalid_end_before_start(self):
        valid, msg = validate_time_range(time(17, 0), time(9, 0))
        assert valid is False

    def test_none_values(self):
        valid, msg = validate_time_range(None, time(17, 0))
        assert valid is False


class TestValidateGoalInput:
    def test_valid_goal(self):
        valid, msg = validate_goal_input("Code 4 hours", "4.0")
        assert valid is True

    def test_empty_title(self):
        valid, msg = validate_goal_input("", "4.0")
        assert valid is False

    def test_zero_hours(self):
        valid, msg = validate_goal_input("Goal", "0")
        assert valid is False

    def test_negative_hours(self):
        valid, msg = validate_goal_input("Goal", "-1")
        assert valid is False

    def test_invalid_hours(self):
        valid, msg = validate_goal_input("Goal", "abc")
        assert valid is False

    def test_over_24_hours(self):
        valid, msg = validate_goal_input("Goal", "25")
        assert valid is False


class TestValidateBlockedList:
    def test_valid_list(self):
        valid, items = validate_blocked_list("facebook.com, youtube.com, reddit.com")
        assert valid is True
        assert len(items) == 3
        assert "facebook.com" in items

    def test_empty_string(self):
        valid, items = validate_blocked_list("")
        assert valid is True
        assert items == []

    def test_whitespace_handling(self):
        valid, items = validate_blocked_list("  fb.com  ,  yt.com  ")
        assert len(items) == 2


class TestFormatSeconds:
    def test_seconds(self):
        assert format_seconds(45) == "45s"

    def test_minutes(self):
        assert format_seconds(125) == "2m 5s"

    def test_hours(self):
        assert format_seconds(3665) == "1h 1m"


class TestFormatScoreColor:
    def test_high_score(self):
        assert format_score_color(85) == "#2ecc71"

    def test_medium_score(self):
        assert format_score_color(65) == "#f39c12"

    def test_low_score(self):
        assert format_score_color(30) == "#e74c3c"

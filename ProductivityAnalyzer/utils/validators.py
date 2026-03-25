# utils/validators.py
"""
Input validation utilities for UI forms and data integrity.
"""

from datetime import time


def validate_time_range(start_time: time, end_time: time) -> tuple[bool, str]:
    """
    Validate that a time range is valid.

    Returns:
        (is_valid, error_message)
    """
    if start_time is None or end_time is None:
        return False, "Start time and end time are required."

    if start_time >= end_time:
        return False, "Start time must be before end time."

    return True, ""


def validate_goal_input(title: str, target_hours: str) -> tuple[bool, str]:
    """
    Validate goal form input.

    Returns:
        (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Goal title is required."

    if len(title.strip()) > 255:
        return False, "Goal title must be under 255 characters."

    try:
        hours = float(target_hours)
        if hours <= 0:
            return False, "Target hours must be greater than 0."
        if hours > 24:
            return False, "Target hours cannot exceed 24."
    except (ValueError, TypeError):
        return False, "Target hours must be a valid number."

    return True, ""


def validate_blocked_list(text: str) -> tuple[bool, list]:
    """
    Parse and validate a comma-separated list of apps/websites.

    Returns:
        (is_valid, cleaned_list)
    """
    if not text or not text.strip():
        return True, []

    items = [item.strip() for item in text.split(",") if item.strip()]
    return True, items


def format_seconds(seconds: int) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_score_color(score: float) -> str:
    """Return a hex color based on productivity score."""
    if score >= 80:
        return "#2ecc71"  # Green
    elif score >= 60:
        return "#f39c12"  # Orange
    elif score >= 40:
        return "#e67e22"  # Dark orange
    return "#e74c3c"  # Red

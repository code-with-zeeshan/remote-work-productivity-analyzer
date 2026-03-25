# config/constants.py
"""
Application-wide constants and enumerations.
"""

from enum import Enum


class AppCategory(Enum):
    """Categories for classifying window/app activity."""

    PRODUCTIVE = "productive"
    UNPRODUCTIVE = "unproductive"
    NEUTRAL = "neutral"
    IDLE = "idle"


class Tables:
    """Database table names."""

    ACTIVITY_LOG = "activity_log"
    FOCUS_SETTINGS = "focus_settings"
    GOALS = "goals"
    APP_CATEGORIES = "app_categories"
    DAILY_SUMMARY = "daily_summary"


class GoalPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Default categorization keywords
PRODUCTIVE_KEYWORDS = [
    "visual studio code",
    "vscode",
    "pycharm",
    "intellij",
    "sublime text",
    "terminal",
    "cmd",
    "powershell",
    "github",
    "gitlab",
    "bitbucket",
    "stackoverflow",
    "jupyter",
    "postman",
    "pgadmin",
    "dbeaver",
    "figma",
    "notion",
    "obsidian",
    "trello",
    "jira",
    "linear",
    "google docs",
    "microsoft word",
    "excel",
    "powerpoint",
    "zoom meeting",
    "teams meeting",
]

UNPRODUCTIVE_KEYWORDS = [
    "youtube",
    "facebook",
    "instagram",
    "twitter",
    "tiktok",
    "reddit",
    "netflix",
    "hulu",
    "disney+",
    "twitch",
    "whatsapp web",
    "telegram web",
    "discord",
    "candy crush",
    "minecraft",
    "steam",
    "amazon shopping",
    "ebay",
    "aliexpress",
]

NEUTRAL_KEYWORDS = [
    "chrome",
    "firefox",
    "edge",
    "safari",
    "brave",
    "outlook",
    "gmail",
    "thunderbird",
    "slack",
    "microsoft teams",
    "zoom",
    "file explorer",
    "finder",
    "settings",
]

# UI Constants
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 700
SIDEBAR_WIDTH = 220
CHART_COLORS = {
    AppCategory.PRODUCTIVE: "#2ecc71",
    AppCategory.UNPRODUCTIVE: "#e74c3c",
    AppCategory.NEUTRAL: "#f39c12",
    AppCategory.IDLE: "#95a5a6",
}

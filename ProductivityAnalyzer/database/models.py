# database/models.py
"""
Data models using dataclasses.
These represent the domain objects used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time

from config.constants import AppCategory, GoalPeriod


@dataclass
class ActivityLog:
    """Represents a single tracked activity entry."""

    id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    window_title: str = ""
    category: AppCategory = AppCategory.NEUTRAL
    duration_seconds: int = 0

    @classmethod
    def from_db_row(cls, row: tuple) -> "ActivityLog":
        """Create from database tuple (id, timestamp, window_title, category, duration_seconds)."""
        return cls(
            id=row[0],
            timestamp=row[1],
            window_title=row[2],
            category=AppCategory(row[3]) if row[3] else AppCategory.NEUTRAL,
            duration_seconds=row[4] if len(row) > 4 else 0,
        )


@dataclass
class FocusSettings:
    """Represents focus mode configuration."""

    id: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    blocked_apps: list[str] = field(default_factory=list)
    blocked_websites: list[str] = field(default_factory=list)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_db_row(cls, row: tuple) -> "FocusSettings":
        """Create from database tuple."""
        return cls(
            id=row[0],
            start_time=row[1],
            end_time=row[2],
            blocked_apps=row[3].split(",") if row[3] else [],
            blocked_websites=row[4].split(",") if row[4] else [],
            is_active=row[5] if len(row) > 5 else False,
            created_at=row[6] if len(row) > 6 else datetime.now(),
        )


@dataclass
class ProductivityGoal:
    """Represents a user-defined productivity goal."""

    id: int | None = None
    title: str = ""
    target_hours: float = 0.0
    period: GoalPeriod = GoalPeriod.DAILY
    current_progress: float = 0.0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def progress_percentage(self) -> float:
        if self.target_hours <= 0:
            return 0.0
        return min(100.0, (self.current_progress / self.target_hours) * 100)

    @classmethod
    def from_db_row(cls, row: tuple) -> "ProductivityGoal":
        return cls(
            id=row[0],
            title=row[1],
            target_hours=float(row[2]),
            period=GoalPeriod(row[3]),
            current_progress=float(row[4]) if row[4] else 0.0,
            is_active=row[5] if len(row) > 5 else True,
            created_at=row[6] if len(row) > 6 else datetime.now(),
        )


@dataclass
class DailySummary:
    """Aggregated daily productivity data."""

    date: date = field(default_factory=date.today)
    productive_seconds: int = 0
    unproductive_seconds: int = 0
    neutral_seconds: int = 0
    idle_seconds: int = 0
    total_entries: int = 0
    score: float = 0.0

    @property
    def total_seconds(self) -> int:
        return self.productive_seconds + self.unproductive_seconds + self.neutral_seconds + self.idle_seconds

    @property
    def productive_minutes(self) -> float:
        return self.productive_seconds / 60

    @property
    def unproductive_minutes(self) -> float:
        return self.unproductive_seconds / 60

    @property
    def grade(self) -> str:
        if self.score >= 90:
            return "A+"
        elif self.score >= 80:
            return "A"
        elif self.score >= 70:
            return "B"
        elif self.score >= 60:
            return "C"
        elif self.score >= 50:
            return "D"
        return "F"

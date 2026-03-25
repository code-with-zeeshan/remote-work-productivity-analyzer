# services/suggestion_engine.py
"""
Generates actionable productivity suggestions based on user activity patterns.
"""

from datetime import date

from database.connection import DatabasePool
from database.models import DailySummary
from database.repositories.activity_repo import ActivityRepository
from reporting.report_generator import ReportGenerator
from utils.logger import setup_logger

logger = setup_logger("services.suggestions")


class Suggestion:
    """A single productivity suggestion."""

    def __init__(self, icon: str, title: str, description: str, priority: str = "info") -> None:
        self.icon = icon
        self.title = title
        self.description = description
        self.priority = priority

    def __repr__(self) -> str:
        return f"[{self.priority.upper()}] {self.icon} {self.title}: {self.description}"


class SuggestionEngine:
    """Analyzes activity data and generates actionable suggestions."""

    def __init__(self, db_pool: DatabasePool) -> None:
        self.db_pool = db_pool
        self.report_gen = ReportGenerator(db_pool)

    def get_suggestions(self) -> list[Suggestion]:
        """Generate suggestions based on today's and recent activity."""
        suggestions: list[Suggestion] = []
        today_summary = self.report_gen.get_daily_summary(date.today())
        weekly = self.report_gen.get_weekly_summaries()

        suggestions.extend(self._analyze_today(today_summary))
        suggestions.extend(self._analyze_weekly_trend(weekly))
        suggestions.extend(self._analyze_work_patterns(today_summary))
        suggestions.extend(self._detect_meeting_overload())

        priority_order = {"critical": 0, "warning": 1, "info": 2, "positive": 3}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 2))

        return (
            suggestions
            if suggestions
            else [
                Suggestion(
                    "Target",
                    "Start Tracking",
                    "Begin tracking your activity to receive personalized suggestions!",
                    "info",
                )
            ]
        )

    def _analyze_today(self, summary: DailySummary) -> list[Suggestion]:
        """Analyze today's data."""
        results: list[Suggestion] = []

        if summary.total_seconds == 0:
            return results

        unprod_pct = (
            (summary.unproductive_seconds / summary.total_seconds * 100) if summary.total_seconds else 0
        )
        prod_pct = (summary.productive_seconds / summary.total_seconds * 100) if summary.total_seconds else 0
        idle_pct = (summary.idle_seconds / summary.total_seconds * 100) if summary.total_seconds else 0

        if unprod_pct > 40:
            results.append(
                Suggestion(
                    "!!",
                    "High Distraction Alert",
                    f"Unproductive time is at {unprod_pct:.0f}% today. Consider enabling Focus Mode.",
                    "critical",
                )
            )
        elif unprod_pct > 25:
            results.append(
                Suggestion(
                    "!",
                    "Rising Distractions",
                    f"Unproductive time is {unprod_pct:.0f}%. Try blocking distracting apps.",
                    "warning",
                )
            )

        if prod_pct > 60:
            results.append(
                Suggestion(
                    "*",
                    "Great Productivity!",
                    f"You're at {prod_pct:.0f}% productive time today. Keep it up!",
                    "positive",
                )
            )

        if idle_pct > 30:
            results.append(
                Suggestion(
                    "z",
                    "Extended Idle Time",
                    f"Idle time is {idle_pct:.0f}%. Try setting smaller work sprints.",
                    "warning",
                )
            )

        if summary.score >= 80:
            results.append(
                Suggestion(
                    "+",
                    "Excellent Score!",
                    f"Your productivity score is {summary.score}/100 ({summary.grade}). Outstanding work!",
                    "positive",
                )
            )
        elif summary.score < 40 and summary.total_seconds > 1800:
            results.append(
                Suggestion(
                    "-",
                    "Low Score",
                    f"Score is {summary.score}/100. Try a focused 25-minute work sprint.",
                    "critical",
                )
            )

        return results

    def _analyze_weekly_trend(self, summaries: list[DailySummary]) -> list[Suggestion]:
        """Analyze weekly trends."""
        results: list[Suggestion] = []
        scores = [s.score for s in summaries if s.total_seconds > 0]

        if len(scores) < 3:
            return results

        avg_score = sum(scores) / len(scores)
        recent_avg = sum(scores[-3:]) / 3

        if recent_avg < avg_score - 10:
            results.append(
                Suggestion(
                    "v",
                    "Declining Trend",
                    f"Your recent score avg ({recent_avg:.0f}) is below your weekly avg ({avg_score:.0f}).",
                    "warning",
                )
            )
        elif recent_avg > avg_score + 10:
            results.append(
                Suggestion(
                    "^",
                    "Improving Trend",
                    f"Recent productivity is trending up! Avg: {recent_avg:.0f} vs weekly: {avg_score:.0f}.",
                    "positive",
                )
            )

        return results

    def _analyze_work_patterns(self, summary: DailySummary) -> list[Suggestion]:
        """General pattern-based suggestions."""
        results: list[Suggestion] = []
        total_hours = summary.total_seconds / 3600

        if total_hours > 10:
            results.append(
                Suggestion(
                    "!!",
                    "Burnout Risk",
                    f"You've tracked {total_hours:.1f} hours today. Remember to take breaks!",
                    "critical",
                )
            )
        elif total_hours > 8:
            results.append(
                Suggestion(
                    "~",
                    "Long Day",
                    f"Over {total_hours:.1f} hours tracked. Consider wrapping up for the day.",
                    "warning",
                )
            )

        return results

    def _detect_meeting_overload(self, target_date: date | None = None) -> list[Suggestion]:
        """Detect if user is spending too much time in meetings."""
        if target_date is None:
            target_date = date.today()

        results: list[Suggestion] = []
        activity_repo = ActivityRepository(self.db_pool)
        top_apps = activity_repo.get_top_apps(target_date, limit=20)

        meeting_keywords = ["zoom", "teams", "meet", "webex", "slack huddle", "discord call"]
        meeting_seconds = 0

        for app in top_apps:
            title_lower = app["window_title"].lower()
            for keyword in meeting_keywords:
                if keyword in title_lower:
                    meeting_seconds += app["total_seconds"]
                    break

        meeting_hours = meeting_seconds / 3600

        if meeting_hours > 5:
            results.append(
                Suggestion(
                    "!!",
                    "Meeting Overload!",
                    f"You've spent {meeting_hours:.1f} hours in meetings today. Try to block focus time.",
                    "critical",
                )
            )
        elif meeting_hours > 3:
            results.append(
                Suggestion(
                    "!",
                    "Heavy Meeting Day",
                    f"{meeting_hours:.1f} hours in meetings. Consider declining non-essential ones.",
                    "warning",
                )
            )

        return results

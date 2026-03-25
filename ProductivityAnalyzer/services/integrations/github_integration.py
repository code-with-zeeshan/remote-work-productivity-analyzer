# services/integrations/github_integration.py
"""
GitHub commit analytics integration.
Fetches commit data from GitHub API to correlate coding output with productivity.
"""

import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from utils.logger import setup_logger

logger = setup_logger("integrations.github")


@dataclass
class CommitData:
    """Represents a single commit."""

    sha: str = ""
    message: str = ""
    timestamp: datetime | None = None
    additions: int = 0
    deletions: int = 0
    repo_name: str = ""

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions


@dataclass
class GitHubDailySummary:
    """Aggregated GitHub data for one day."""

    date: date = field(default_factory=date.today)
    total_commits: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    repos_contributed: list[str] = field(default_factory=list)
    commits: list[CommitData] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return self.total_additions + self.total_deletions

    @property
    def coding_score(self) -> float:
        """Simple coding productivity score (0-100)."""
        if self.total_commits == 0:
            return 0.0
        commit_score = min(50, self.total_commits * 10)
        change_score = min(50, self.total_changes / 20)
        return min(100, commit_score + change_score)


class GitHubIntegration:
    """Fetches and analyzes GitHub commit data."""

    API_BASE = "https://api.github.com"

    def __init__(self, token: str | None = None, username: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.username = username or os.getenv("GITHUB_USERNAME", "")
        self._session = None

    def _get_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ProductivityAnalyzer/2.0",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def _request(self, url: str) -> list | None:
        """Make a GET request to GitHub API."""
        try:
            import requests

            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                result: list = response.json()
                return result
            elif response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return None
            elif response.status_code == 401:
                logger.error("GitHub authentication failed. Check your token.")
                return None
            else:
                logger.error(f"GitHub API error: {response.status_code}")
                return None
        except ImportError:
            logger.error("requests library not installed")
            return None
        except Exception as e:
            logger.error(f"GitHub API request failed: {e}")
            return None

    def get_user_events(self, days: int = 7) -> list[CommitData]:
        """Fetch recent push events for the user."""
        if not self.username:
            logger.warning("GitHub username not configured")
            return []

        url = f"{self.API_BASE}/users/{self.username}/events?per_page=100"
        events = self._request(url)

        if not events:
            return []

        commits: list[CommitData] = []
        cutoff = datetime.now() - timedelta(days=days)

        for event in events:
            if event.get("type") != "PushEvent":
                continue

            created_at = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if created_at < cutoff:
                continue

            repo_name = event.get("repo", {}).get("name", "unknown")
            payload_commits = event.get("payload", {}).get("commits", [])

            for commit in payload_commits:
                commits.append(
                    CommitData(
                        sha=commit.get("sha", "")[:7],
                        message=commit.get("message", "").split("\n")[0][:80],
                        timestamp=created_at,
                        repo_name=repo_name,
                    )
                )

        logger.info(f"Fetched {len(commits)} commits from GitHub (last {days} days)")
        return commits

    def get_daily_summary(self, target_date: date | None = None) -> GitHubDailySummary:
        """Get commit summary for a specific day."""
        if target_date is None:
            target_date = date.today()

        all_commits = self.get_user_events(days=7)
        day_commits = [
            c for c in all_commits if c.timestamp is not None and c.timestamp.date() == target_date
        ]

        repos = list(set(c.repo_name for c in day_commits))

        return GitHubDailySummary(
            date=target_date,
            total_commits=len(day_commits),
            total_additions=sum(c.additions for c in day_commits),
            total_deletions=sum(c.deletions for c in day_commits),
            repos_contributed=repos,
            commits=day_commits,
        )

    def get_weekly_commit_counts(self) -> list[dict[str, object]]:
        """Get commit count per day for the last 7 days."""
        all_commits = self.get_user_events(days=7)
        today = date.today()
        results: list[dict[str, object]] = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = sum(1 for c in all_commits if c.timestamp is not None and c.timestamp.date() == day)
            results.append({"date": day, "commits": count})

        return results

    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured."""
        return bool(self.username)

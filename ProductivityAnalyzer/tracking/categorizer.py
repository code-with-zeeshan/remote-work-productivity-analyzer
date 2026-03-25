# tracking/categorizer.py
"""
Categorizes window titles into productivity categories.
Loads rules from database and falls back to defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from config.constants import (
    NEUTRAL_KEYWORDS,
    PRODUCTIVE_KEYWORDS,
    UNPRODUCTIVE_KEYWORDS,
    AppCategory,
)
from utils.logger import setup_logger

if TYPE_CHECKING:
    from database.connection import DatabasePool

logger = setup_logger("tracking.categorizer")


class AppCategorizer:
    """Categorizes applications/windows as productive, unproductive, neutral, or idle."""

    def __init__(self, db_pool: DatabasePool | None = None) -> None:
        self.db_pool: DatabasePool | None = db_pool
        self.rules: dict[str, AppCategory] = {}
        self._load_default_rules()
        if db_pool:
            self._load_db_rules()

    def _load_default_rules(self) -> None:
        """Load built-in default rules."""
        for keyword in PRODUCTIVE_KEYWORDS:
            self.rules[keyword.lower()] = AppCategory.PRODUCTIVE
        for keyword in UNPRODUCTIVE_KEYWORDS:
            self.rules[keyword.lower()] = AppCategory.UNPRODUCTIVE
        for keyword in NEUTRAL_KEYWORDS:
            self.rules[keyword.lower()] = AppCategory.NEUTRAL

    def _load_db_rules(self) -> None:
        """Load custom rules from the database (overrides defaults)."""
        if self.db_pool is None:
            return
        try:
            rows = self.db_pool.fetch_all("SELECT keyword, category FROM app_categories")
            for row in rows:
                keyword = row[0].lower().strip()
                try:
                    category = AppCategory(row[1])
                    self.rules[keyword] = category
                except ValueError:
                    logger.warning(f"Unknown category '{row[1]}' for keyword '{keyword}'")
            logger.info(f"Loaded {len(rows)} category rules from database")
        except Exception as e:
            logger.warning(f"Could not load DB rules, using defaults: {e}")

    def categorize(self, window_title: str) -> AppCategory:
        """Categorize a window title."""
        if not window_title or window_title in ("No Active Window", "Error", ""):
            return AppCategory.IDLE

        title_lower = window_title.lower()

        for keyword, category in self.rules.items():
            if keyword in title_lower:
                return category

        return AppCategory.NEUTRAL

    def add_rule(self, keyword: str, category: AppCategory) -> bool:
        """Add or update a categorization rule."""
        keyword = keyword.lower().strip()
        self.rules[keyword] = category

        if self.db_pool is not None:
            try:
                self.db_pool.execute_query(
                    """
                    INSERT INTO app_categories (keyword, category)
                    VALUES (%s, %s)
                    ON CONFLICT (keyword) DO UPDATE SET category = EXCLUDED.category
                    """,
                    (keyword, category.value),
                )
                logger.info(f"Rule saved: '{keyword}' -> {category.value}")
                return True
            except Exception as e:
                logger.error(f"Failed to save rule: {e}")
                return False
        return True

    def remove_rule(self, keyword: str) -> bool:
        """Remove a categorization rule."""
        keyword = keyword.lower().strip()
        self.rules.pop(keyword, None)

        if self.db_pool is not None:
            return self.db_pool.execute_query("DELETE FROM app_categories WHERE keyword = %s", (keyword,))
        return True

    def get_all_rules(self) -> dict[str, str]:
        """Return all rules as keyword -> category string dict."""
        return {k: v.value for k, v in sorted(self.rules.items())}

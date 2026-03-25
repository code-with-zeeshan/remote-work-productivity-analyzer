# tests/test_tracking/test_categorizer.py
"""Tests for AppCategorizer."""

from config.constants import AppCategory
from tracking.categorizer import AppCategorizer


class TestAppCategorizer:
    def setup_method(self):
        self.categorizer = AppCategorizer(db_pool=None)

    def test_productive_apps(self):
        assert self.categorizer.categorize("Visual Studio Code - main.py") == AppCategory.PRODUCTIVE
        assert self.categorizer.categorize("PyCharm - project") == AppCategory.PRODUCTIVE
        assert self.categorizer.categorize("GitHub - Pull Request") == AppCategory.PRODUCTIVE

    def test_unproductive_apps(self):
        assert self.categorizer.categorize("YouTube - Funny Videos") == AppCategory.UNPRODUCTIVE
        assert self.categorizer.categorize("Facebook - News Feed") == AppCategory.UNPRODUCTIVE
        assert self.categorizer.categorize("Reddit - r/memes") == AppCategory.UNPRODUCTIVE

    def test_neutral_apps(self):
        assert self.categorizer.categorize("Google Chrome") == AppCategory.NEUTRAL
        assert self.categorizer.categorize("Slack - Messages") == AppCategory.NEUTRAL

    def test_idle(self):
        assert self.categorizer.categorize("") == AppCategory.IDLE
        assert self.categorizer.categorize("No Active Window") == AppCategory.IDLE
        assert self.categorizer.categorize(None) == AppCategory.IDLE

    def test_unknown_app(self):
        assert self.categorizer.categorize("Some Random App") == AppCategory.NEUTRAL

    def test_add_rule(self):
        self.categorizer.add_rule("my_special_app", AppCategory.PRODUCTIVE)
        assert self.categorizer.categorize("my_special_app - window") == AppCategory.PRODUCTIVE

    def test_remove_rule(self):
        self.categorizer.add_rule("temp_app", AppCategory.UNPRODUCTIVE)
        assert self.categorizer.categorize("temp_app running") == AppCategory.UNPRODUCTIVE
        self.categorizer.remove_rule("temp_app")
        assert self.categorizer.categorize("temp_app running") == AppCategory.NEUTRAL

    def test_case_insensitivity(self):
        assert self.categorizer.categorize("YOUTUBE - Video") == AppCategory.UNPRODUCTIVE
        assert self.categorizer.categorize("visual studio CODE") == AppCategory.PRODUCTIVE

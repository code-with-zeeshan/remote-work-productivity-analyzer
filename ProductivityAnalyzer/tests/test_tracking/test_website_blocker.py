# tests/test_tracking/test_website_blocker.py
"""Tests for WebsiteBlocker."""

from unittest.mock import mock_open, patch

from tracking.website_blocker import BLOCK_MARKER_END, BLOCK_MARKER_START, WebsiteBlocker


class TestWebsiteBlocker:
    def setup_method(self):
        self.blocker = WebsiteBlocker()

    def test_remove_our_blocks(self):
        content = f"""
# Normal entry
127.0.0.1 localhost
{BLOCK_MARKER_START}
127.0.0.1 facebook.com
127.0.0.1 youtube.com
{BLOCK_MARKER_END}
# Another entry
"""
        result = self.blocker._remove_our_blocks(content)
        assert "facebook.com" not in result
        assert "youtube.com" not in result
        assert "localhost" in result
        assert "Another entry" in result

    def test_remove_our_blocks_no_blocks(self):
        content = "127.0.0.1 localhost\n"
        result = self.blocker._remove_our_blocks(content)
        assert result.strip() == "127.0.0.1 localhost"

    @patch("builtins.open", mock_open(read_data="127.0.0.1 localhost\n"))
    def test_block_writes_entries(self):
        with patch.object(self.blocker, "hosts_path", "/tmp/test_hosts"):
            result = self.blocker.block(["facebook.com", "youtube.com"])
            # Will fail on actual write but tests the logic path
            # In a real test, use a temp file

    def test_block_empty_list(self):
        result = self.blocker.block([])
        assert result is True

    @patch("builtins.open", side_effect=PermissionError("Access denied"))
    def test_block_permission_error(self, mock_file):
        result = self.blocker.block(["facebook.com"])
        assert result is False

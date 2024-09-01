import unittest
from unittest.mock import patch
from modules.tracker import get_active_window_title

class TestTracker(unittest.TestCase):
    @patch('pygetwindow.getActiveWindow')
    def test_get_active_window_title(self,mock_get_active_window):
       # Mock the return value
        mock_get_active_window.return_value.title = "Test Window"
        title = get_active_window_title()
        self.assertEqual(title, "Test Window")

if __name__ == '__main__':
    unittest.main()

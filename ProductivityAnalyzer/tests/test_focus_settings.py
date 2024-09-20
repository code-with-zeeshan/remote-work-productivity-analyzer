import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from PyQt5.QtCore import QTime  # Import QTime from PyQt5 or PySide2 if using PySide2
from modules.ui import ProductivityAnalyzerApp

# Adjust sys.path if necessary
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))


class TestFocusSettings(unittest.TestCase):

    def setUp(self):
        self.app = ProductivityAnalyzerApp()
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.cursor.return_value = self.cursor

    @patch('modules.database.save_focus_settings')
    def test_save_focus_settings(self, mock_save_focus_settings):
        # Create QTime objects from the time strings
        start_time = QTime.fromString('09:00', 'HH:mm')
        end_time = QTime.fromString('17:00', 'HH:mm')

        # Set the time using QTime objects
        self.app.focus_start_time.setTime(start_time)
        self.app.focus_end_time.setTime(end_time)
        self.app.blocked_apps_input.setText('app1,app2')
        self.app.blocked_websites_input.setText('site1,site2')

        # Pass the parameters directly to the save_focus_settings method
        self.app.save_focus_settings(
            start_time.toString('HH:mm'),
            end_time.toString('HH:mm'),
            self.app.blocked_apps_input.text(),
            self.app.blocked_websites_input.text()
        )

        mock_save_focus_settings.assert_called_once_with(
            self.conn,
            '09:00',
            '17:00',
            'app1,app2',
            'site1,site2'
        )

if __name__ == '__main__':
    unittest.main()

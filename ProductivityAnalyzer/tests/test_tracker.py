
import unittest
from unittest.mock import patch, MagicMock
from ..modules.ui import ProductivityAnalyzerApp





class TestTrackingFunctionality(unittest.TestCase):

    @patch('modules.tracker.get_active_window_title')
    @patch('modules.database.log_activity_to_db')
    def test_track_activity(self, mock_log_activity_to_db, mock_get_active_window_title):
        mock_get_active_window_title.return_value = 'Test Window'
        app = ProductivityAnalyzerApp()
        app.tracking = True
        app.tracking_thread = MagicMock()

        with patch('time.sleep', return_value=None):
            with patch('PyQt5.QtWidgets.QApplication.processEvents', return_value=None):
                app.track_activity()

        mock_log_activity_to_db.assert_called()
        self.assertEqual(mock_get_active_window_title.call_count, 1)

if __name__ == '__main__':
    unittest.main()

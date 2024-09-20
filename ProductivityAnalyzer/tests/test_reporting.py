import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication
from reporting import ProductivityAnalyzerApp

class TestProductivityAnalyzerApp(unittest.TestCase):

    def setUp(self):
        # Initialize the QApplication instance (required for PyQt5)
        self.app = QApplication([])  
        self.analyzer = ProductivityAnalyzerApp()
    
    @patch('reporting.sqlite3.connect')
    @patch('reporting.pd.read_sql_query')
    @patch('reporting.pd.to_datetime')
    @patch('reporting.FigureCanvas')
    @patch('reporting.QMainWindow')
    def test_show_chart(self, MockQMainWindow, MockFigureCanvas, MockToDatetime, MockReadSqlQuery, MockConnect):
        # Mock the database connection and query results
        mock_conn = MagicMock()
        MockConnect.return_value = mock_conn
        
        # Create mock DataFrame
        mock_df = pd.DataFrame({
            'timestamp': ['2024-09-01 12:00:00', '2024-09-01 13:00:00'],
            'window_title': ['App1', 'App2']
        })
        MockReadSqlQuery.return_value = mock_df
        
        # Mock the to_datetime function
        MockToDatetime.return_value = pd.to_datetime(mock_df['timestamp'])
        
        # Mock FigureCanvas and QMainWindow
        mock_canvas = MagicMock()
        MockFigureCanvas.return_value = mock_canvas
        mock_window = MagicMock()
        MockQMainWindow.return_value = mock_window
        
        # Call the method
        self.analyzer.show_chart()
        
        # Check that database connection was established
        MockConnect.assert_called_once_with('activity_log.db')
        
        # Check that the DataFrame was read from the SQL query
        MockReadSqlQuery.assert_called_once_with("SELECT * FROM activity_log", mock_conn)
        
        # Check that the figure canvas was created
        MockFigureCanvas.assert_called_once()
        
        # Check that QMainWindow was created and showed
        MockQMainWindow.assert_called_once()
        mock_window.show.assert_called_once()

if __name__ == '__main__':
    unittest.main()

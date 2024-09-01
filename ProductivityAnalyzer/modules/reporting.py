# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains  Manages data visualization and reporting features. for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import sqlite3
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class ProductivityAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()

    def show_chart(self):
        try:
            conn = sqlite3.connect('activity_log.db')
            df = pd.read_sql_query("SELECT * FROM activity_log", conn)
            conn.close()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return

        # Ensure the 'timestamp' column exists
        if 'timestamp' not in df.columns:
            print("Column 'timestamp' not found in DataFrame")
            return

        try:
            # Convert 'timestamp' to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['Date'] = df['timestamp'].dt.date
            activity_summary = df.groupby('Date')['window_title'].count()
        except ValueError as e:
            print(f"Error converting timestamp: {e}")
            return

        # Create the chart
        fig, ax = plt.subplots()
        activity_summary.plot(kind='bar', ax=ax, title='Activity Summary')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')

        # Display the chart in a QMainWindow
        canvas = FigureCanvas(fig)
        chart_window = QMainWindow(self)
        chart_window.setCentralWidget(canvas)
        chart_window.setWindowTitle("Activity Summary Chart")
        chart_window.resize(800, 600)  # Set a size for the chart window
        chart_window.show()

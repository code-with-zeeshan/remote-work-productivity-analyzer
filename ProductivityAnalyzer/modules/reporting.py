# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains data visualization and reporting features for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

import asyncio
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import  QTimer
from modules.database import Database
from matplotlib.figure import Figure

class ProductivityAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        print("Database initialized:", self.db)  # Debugging statement

    def some_method(self):
        print("Accessing database:", self.db)  # Debugging statement before access
        # Access self.db here

    async def fetch_all_data_async(self):
        """Fetch all data asynchronously."""
        
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, activity FROM activity_log")
            data = cursor.fetchall()
            self.db.close_connection(conn)
            return data
        except Exception as e:
            print(f"Error fetching data asynchronously: {e}")
            return []

    async def generate_report_async(self):  # Renamed method to avoid conflict
        """Generate the report asynchronously."""
        data = await self.fetch_all_data_async()
        self.create_visualization(data)

    def create_visualization(self, data):
        """Create visualization from data."""
        df = pd.DataFrame(data, columns=['id', 'timestamp', 'activity'])
        
        # Ensure the 'timestamp' column exists
        if 'timestamp' not in df.columns:
            print("Column 'timestamp' not found in DataFrame")
            return
        
        try:
            # Convert 'timestamp' to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['Date'] = df['timestamp'].dt.date #use 'activity' instead of 'window_title'
            activity_summary = df.groupby('Date')['activity'].count() #Uptated column name
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
        layout = QVBoxLayout()  # Assuming QVBoxLayout, you can choose the layout that fits your needs
        self.setLayout(layout)  # Set the layout to the widget
        layout.addWidget(canvas)  # Add the canvas to the layout
        chart_window = QMainWindow(self)
        chart_window.setCentralWidget(canvas)
        chart_window.setWindowTitle("Activity Summary Chart")
        chart_window.resize(800, 600)  # Set a size for the chart window
        chart_window.show()

    def show_chart(self):
        """Fetch data and show chart."""
        

        def trigger_async_report():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.generate_report())
            loop.close()

        QTimer.singleShot(0, trigger_async_report)

    async def generate_report(self):
        figure = Figure()
        ax = figure.add_subplot(111)
        ax.pie([20, 30, 50], labels=["Work", "Break", "Other"], autopct="%1.1f%%")
    
        canvas = FigureCanvas(figure)
        layout = QVBoxLayout()  # Assuming QVBoxLayout, you can choose the layout that fits your needs
        self.setLayout(layout)  # Set the layout to the widget
        layout.addWidget(canvas)  # Add the canvas to the layout


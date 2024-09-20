# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeeshan
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains UI components for the Remote Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, 
    QFormLayout, QTimeEdit, QLineEdit, QMessageBox, QMainWindow, 
    QMenuBar, QMenu, QHBoxLayout, QLabel, QAction
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
import threading
import time
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from modules.tracker import get_active_window_title, FocusTrackerApp  # Ensure FocusTrackerApp is correctly imported
from modules.database import Database  # Used for all database operations in this module

class Communicator(QObject):
    update_log_signal = pyqtSignal(str)



class ProductivityAnalyzerHome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Remote Work Productivity Analyzer') # Set window title
        self.setGeometry(300, 100, 1000, 600)

       # Create the top menu bar
        self.create_menu_bar()
        
        # Set the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        welcome_label = QLabel("Welcome to the Productivity Analyzer!")
        layout.addWidget(welcome_label)

        # Create a horizontal layout for the top navigation buttons
        top_navigation_layout = QHBoxLayout()
        focus_mode_button = QPushButton("Start Focus Mode")
        reports_button = QPushButton("Reports")
        activity_log_button = QPushButton("Activity Logs")
        top_navigation_layout.addWidget(focus_mode_button)
        top_navigation_layout.addWidget(reports_button)
        top_navigation_layout.addWidget(activity_log_button)

        # Add top navigation to the main layout
        layout.addLayout(top_navigation_layout)

       # Recent activities and productivity stats
        self.recent_activity_display = QTextEdit()
        self.recent_activity_display.setReadOnly(True)
        layout.addWidget(QLabel("Recent Activities"))
        layout.addWidget(self.recent_activity_display)
        
        layout.addWidget(QLabel("Productivity Stats"))
        layout.addWidget(QLabel("Chart Placeholder"))
        

        # Connect buttons to functionalities
        focus_mode_button.clicked.connect(self.start_focus_mode)
        reports_button.clicked.connect(self.view_reports)
        activity_log_button.clicked.connect(self.view_activity_logs)

    def create_menu_bar(self):
        menubar = self.menuBar()
        profile_menu = menubar.addMenu("Profile")
        settings_menu = menubar.addMenu("Settings")

        # Adding actions to the settings menu
        view_settings_action = QAction("View Settings", self)
        view_settings_action.triggered.connect(self.view_settings)
        settings_menu.addAction(view_settings_action)
    def start_focus_mode(self):
        # Trigger the focus mode functionality from tracker.py
        blocked_websites = ["facebook.com", "youtube.com"]
        focus_tracker = FocusTrackerApp()
        focus_tracker.start_focus_session(blocked_websites)
        print("Focus Mode Started")

    def view_reports(self):
        print("View Reports")
        # Code to view reports

    def view_activity_logs(self):
        print("View Activity Logs")
        # Code to show activity logs

    def view_settings(self):
        print("View Settings")
        # Code to view settings

class ProductivityAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_search)
        self.timer.setSingleShot(True)
        self.tracking = False
        self.tracking_thread = None
        self.tracker_app = FocusTrackerApp()  # Corrected from TrackerApp to FocusTrackerApp

        # Create a "Start Focus Mode" button in the UI
        self.focus_mode_button = QPushButton("Start Focus Mode", self)
        self.focus_mode_button.clicked.connect(self.on_focus_mode_button_clicked)


        # Initialize the Database once and keep the connection consistent
        self.db = Database()
        self.db_connection = self.db.get_connection()

        # Ensure proper connection handling
        
        if self.db_connection is None:
            raise Exception("Database connection failed!")

        self.communicator = Communicator()
        self.communicator.update_log_signal.connect(self.update_log_area)

    def apply_stylesheet(self):
        try:
            with open("style.qss", "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Warning: 'style.qss' file not found. Using default stylesheet.")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def initUI(self):
        self.apply_stylesheet()
        self.setWindowTitle('Remote Work Productivity Analyzer')

        layout = QVBoxLayout()
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.focus_start_time = QTimeEdit()
        self.focus_end_time = QTimeEdit()
        self.blocked_apps_input = QLineEdit()
        self.blocked_websites_input = QLineEdit()

        

        self.save_focus_settings_button = QPushButton('Save Focus Settings')
        self.save_focus_settings_button.clicked.connect(self.save_focus_settings)
        layout.addWidget(self.save_focus_settings_button)

        self.start_focus_mode_button = QPushButton('Start Focus Mode')
        self.start_focus_mode_button.clicked.connect(self.start_focus_mode)
        layout.addWidget(self.start_focus_mode_button)

        self.stop_focus_mode_button = QPushButton('Stop Focus Mode')
        self.stop_focus_mode_button.clicked.connect(self.stop_focus_mode)
        layout.addWidget(self.stop_focus_mode_button)

        self.setLayout(layout)

    def create_focus_form(self):
        layout = QVBoxLayout()
        focus_form_layout = QFormLayout()
        focus_form_layout.addRow("Focus Start Time:", self.focus_start_time)
        focus_form_layout.addRow("Focus End Time:", self.focus_end_time)
        focus_form_layout.addRow("Blocked Apps (comma separated):", self.blocked_apps_input)
        focus_form_layout.addRow("Blocked Websites (comma separated):", self.blocked_websites_input)
        layout.addLayout(focus_form_layout) 
        return focus_form_layout   

    def on_search_input(self, text):
        """Handle the input text and start the debounce timer."""
        self.current_search_text = text  # Store the current text
        self.timer.stop()  # Stop the timer if it's still running
        self.timer.start(300)  # Debounce time (in milliseconds)

    def on_search(self):
        """Perform search or other actions when timer times out."""
        search_text = self.search_input.text()
        # Handle search logic here
        print(f"Search triggered for: {search_text}")

    def on_focus_mode_button_clicked(self):
        # User clicked the button to save focus mode settings
        self.start_focus_mode()    

    def start_focus_mode(self):
        try:
             self.db_connection = self.db.get_connection()  # Ensure the connection is established
             if self.db_connection is None:
                 raise Exception("Database connection failed!")
             
             start_time = self.focus_start_time.time().toString("HH:mm")
             end_time = self.focus_end_time.time().toString("HH:mm")
             blocked_apps = self.blocked_apps_input.text().split(',')
             blocked_websites = self.blocked_websites_input.text().split(',')

             blocked_apps_str = ','.join(blocked_apps)
             blocked_websites_str = ','.join(blocked_websites)

            
             self.db.save_focus_settings(start_time, end_time, blocked_apps_str, blocked_websites_str)
             self.tracker_app.start_focus_session(blocked_websites)
             print("Focus Mode Started")
        except Exception as e:
             QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def stop_focus_mode(self):
        self.tracker_app.end_focus_session()
        print("Focus Mode Stopped")

    def save_focus_settings(self,start_time, end_time, blocked_apps, blocked_websites):
        try:
            if self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    INSERT INTO focus_settings (end_time, blocked_apps, blocked_websites)
                    VALUES (?, ?, ?,?)
                    ON CONFLICT (your_conflict_column) 
                    DO UPDATE SET end_time = EXCLUDED.end_time, 
                    blocked_apps = EXCLUDED.blocked_apps, 
                    blocked_websites = EXCLUDED.blocked_websites
                 ''', (start_time, end_time, ','.join(blocked_apps), ','.join(blocked_websites)))

                self.db_connection.commit()
            else:
                print("Error: Database connection is not established")
        except Exception as e:
            print(f"Error saving focus settings: {e}")

    def start_tracking(self):
        if not self.tracking:
          conn = self.db.get_connection()  # Correct usage to get a connection from the pool
 
          if conn is None:
            print("Failed to connect to database.")
            return
        
          self.tracking = True
          self.tracking_thread = threading.Thread(target=self.track_activity, args=(conn,))
          self.tracking_thread.start()

    def stop_tracking(self):
        """Stops the tracking thread."""
        if self.tracking:
            self.tracking = False
            if self.tracking_thread:
                self.tracking_thread.join()  # Wait for the tracking thread to finish
            print("Tracking stopped.")
        else:
            print("Tracking is not running.")      

    def track_activity(self):
       conn = self.db.get_connection()  # Each thread should manage its own connection
       while self.tracking:
          active_title = get_active_window_title()
          current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

          self.db.log_activity(current_time, active_title)

          self.communicator.update_log_signal.emit(f"{current_time}: {active_title}")
          QApplication.processEvents()
          time.sleep(5)

       self.db.close_connection(conn)  # Return the connection to the pool

    def log_activity(self, activity):
        if not activity:
            activity = "Unknown"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {activity}\n"
        self.log_area.append(log_entry)
        self.communicator.update_log_signal.emit(log_entry)

    def update_log_area(self, log_message):
        """Updates the log area with a new log message."""
        # Assuming you have a QTextEdit or similar widget to display logs
        self.log_area.append(log_message)  # Append the new log message to the log area
        print(f"Log updated: {log_message}")


    def export_report(self):
        try:
            conn = sqlite3.connect('activity_log.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM activity_log')
            data = cursor.fetchall()
            conn.close()

            if not data:
              print("No data to export")
              return

            df = pd.DataFrame(data, columns=['ID', 'Timestamp', 'Window Title'])
            df.to_csv('activity_report.csv', index=False)
            print("Report exported to activity_report.csv")
        except Exception as e:
            print(f"Error exporting report: {e}")

    def show_chart(self):
        try:
            conn = sqlite3.connect('activity_log.db')
            df = pd.read_sql_query("SELECT * FROM activity_log", conn)
            conn.close()

            df.columns = [col.lower() for col in df.columns]  # Ensure all columns are lowercase
            if 'Timestamp' not in df.columns:
                print("Column 'Timestamp' not found in DataFrame")
                return

            df.columns = ['ID', 'Timestamp', 'Window Title']
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df['Date'] = df['Timestamp'].dt.date
            activity_summary = df.groupby('Date')['Window Title'].count()

            fig, ax = plt.subplots()
            activity_summary.plot(kind='bar', ax=ax, title='Activity Summary')

            canvas = FigureCanvas(fig)
            chart_window = QMainWindow(self)
            chart_window.setCentralWidget(canvas)
            chart_window.setWindowTitle("Activity Summary Chart")
            chart_window.resize(800, 600)
            chart_window.show()
        except Exception as e:
            print(f"Error displaying chart: {e}")

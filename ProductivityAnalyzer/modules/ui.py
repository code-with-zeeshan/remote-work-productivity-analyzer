# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeeshan
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains the UI components for the Remote Work 
# Productivity Analyzer application.
# ----------------------------------------------------------------------------


from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFormLayout, QTimeEdit, QLineEdit, QMessageBox,QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject
import threading
import time
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from modules.tracker import get_active_window_title, FocusTrackerApp as TrackerApp
from modules.database import connect_db, create_table_if_not_exists, log_activity_to_db, save_focus_settings

class Communicator(QObject):
    update_log_signal = pyqtSignal(str)

class ProductivityAnalyzerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = None
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
        self.db_connection = connect_db()

        layout = QVBoxLayout()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.start_time_edit = QTimeEdit()
        layout.addWidget(self.start_time_edit)

        self.end_time_edit = QTimeEdit()
        layout.addWidget(self.end_time_edit)

        self.start_button = QPushButton('Start Tracking')
        self.start_button.clicked.connect(self.start_tracking)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Tracking')
        self.stop_button.clicked.connect(self.stop_tracking)
        layout.addWidget(self.stop_button)

        self.export_button = QPushButton('Export Report')
        self.export_button.clicked.connect(self.export_report)
        layout.addWidget(self.export_button)

        self.show_chart_button = QPushButton('Show Chart')
        self.show_chart_button.clicked.connect(self.show_chart)
        layout.addWidget(self.show_chart_button)

        self.focus_start_time = QTimeEdit()
        self.focus_end_time = QTimeEdit()
        self.blocked_apps_input = QLineEdit()
        self.blocked_websites_input = QLineEdit()

        focus_form_layout = QFormLayout()
        focus_form_layout.addRow("Focus Start Time:", self.focus_start_time)
        focus_form_layout.addRow("Focus End Time:", self.focus_end_time)
        focus_form_layout.addRow("Blocked Apps (comma separated):", self.blocked_apps_input)
        focus_form_layout.addRow("Blocked Websites (comma separated):", self.blocked_websites_input)

        layout.addLayout(focus_form_layout)

        self.save_focus_settings_button = QPushButton('Save Focus Settings')
        self.save_focus_settings_button.clicked.connect(self.save_focus_settings)
        layout.addWidget(self.save_focus_settings_button)

        self.start_button = QPushButton('Start Focus Mode')
        self.start_button.clicked.connect(self.start_focus_mode)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Focus Mode')
        self.stop_button.clicked.connect(self.stop_focus_mode)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.tracking = False
        self.tracking_thread = None
        self.tracker_app = TrackerApp()

    def start_focus_mode(self):
        start_time = self.focus_start_time.time().toString("HH:mm")
        end_time = self.focus_end_time.time().toString("HH:mm")
        blocked_apps = self.blocked_apps_input.text().split(',')
        blocked_websites = self.blocked_websites_input.text().split(',')

        # Join lists into comma-separated strings
        blocked_apps_str = ','.join(blocked_apps)
        blocked_websites_str = ','.join(blocked_websites)

        if self.db_connection:
            try:
                save_focus_settings(self.db_connection, start_time, end_time, blocked_apps_str, blocked_websites_str)
                QMessageBox.information(self, "Settings Saved", "Focus settings have been saved.")
            except Exception as e:
                print(f"Error saving focus settings: {e}")

        self.tracker_app.start_focus_session(blocked_websites)

    def stop_focus_mode(self):
        self.tracker_app.end_focus_session()

    def save_focus_settings(self):
        start_time = self.focus_start_time.time().toString("HH:mm")
        end_time = self.end_time_edit.time().toString("HH:mm")
        blocked_apps = self.blocked_apps_input.text().split(',')
        blocked_websites = self.blocked_websites_input.text().split(',')

        # Join lists into comma-separated strings
        blocked_apps_str = ','.join(blocked_apps)
        blocked_websites_str = ','.join(blocked_websites)

        if self.db_connection:
            try:
                save_focus_settings(self.db_connection, start_time, end_time, blocked_apps_str, blocked_websites_str)
                QMessageBox.information(self, "Settings Saved", "Focus settings have been saved.")
            except Exception as e:
                print(f"Error saving focus settings: {e}")

    def update_log_area(self, message):
        self.log_area.append(message)

    def start_tracking(self):
        if not self.tracking:
            self.tracking = True
            self.tracking_thread = threading.Thread(target=self.track_activity)
            self.tracking_thread.start()

    def stop_tracking(self):
        if self.tracking:
            self.tracking = False
            if self.tracking_thread is not None:
                self.tracking_thread.join()

    def track_activity(self):
        conn = connect_db()
        if not conn:
            print("Failed to connect to database.")
            return
        
        cursor = conn.cursor()
        create_table_if_not_exists(cursor)

        while self.tracking:
            active_title = get_active_window_title()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_activity_to_db(conn, current_time, active_title)

            # Emit signal to update the log area
            self.communicator.update_log_signal.emit(f"{current_time}: {active_title}")

            QApplication.processEvents()
            time.sleep(5)

        conn.close()

    def export_report(self):
        try:
            conn = sqlite3.connect('activity_log.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM activity_log')
            data = cursor.fetchall()
            conn.close()

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

            if 'Timestamp' not in df.columns:
                print("Column 'Timestamp' not found in DataFrame")
                return

            # Correct the column names in the DataFrame
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

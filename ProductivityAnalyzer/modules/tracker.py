# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains the tracking functionality for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

# modules/tracker.py

import datetime
import sqlite3
import pygetwindow as gw
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox
import time
import threading

# Path to the hosts file (might be different on Linux/Mac)
HOSTS_PATH = 'C:/Users/DELL/personalproject/project2/ProductivityAnalyzer/hosts_backup.txt'
REDIRECT_IP = '127.0.0.1'

def get_focus_settings():
    conn = sqlite3.connect('activity_log.db')
    cursor = conn.cursor()
    cursor.execute("SELECT start_time, end_time, blocked_apps, blocked_websites FROM focus_settings ORDER BY id DESC LIMIT 1")
    settings = cursor.fetchone()
    conn.close()
    return settings

def get_active_window_title():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            title = active_window.title
            if title == "Remote Work Productivity Analyzer":
                return "No Active Window"  # Skip logging if it's the analyzer itself
            return title
        else:
            return "No Active Window"
    except Exception as e:
        print(f"Error retrieving active window: {e}")
        return "Error"

class FocusTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tracking = False
        self.tracking_active = False
        self.blocked_websites = []
        self.activity_log = []

    def block_apps(self):
        while self.tracking_active:
            try:
                current_time = datetime.datetime.now().time()
                focus_settings = get_focus_settings()
                if focus_settings:
                    start_time = datetime.datetime.strptime(focus_settings[0], "%H:%M").time()
                    end_time = datetime.datetime.strptime(focus_settings[1], "%H:%M").time()
                    apps_to_block = focus_settings[2].split(',')  # Renamed to avoid conflict
                    blocked_websites = focus_settings[3].split(',')

                    if start_time <= current_time <= end_time:
                        active_title = get_active_window_title()
                        for app in apps_to_block:
                            if app in active_title:
                                windows = gw.getWindowsWithTitle(active_title)
                                if windows:
                                    window = windows[0]
                                    window.minimize()
                                    print(f"Blocking app: {app}")
                time.sleep(1)
            except Exception as e:
                print(f"Error in block_apps: {e}")
                time.sleep(5)  # Avoid rapid retrying in case of an error

    def block_websites(self):
        """Block websites by redirecting them to localhost in the hosts file."""
        try:
            with open(HOSTS_PATH, 'r+') as hosts_file:
             content = hosts_file.read()
            for website in self.blocked_websites:
                if website not in content:
                    hosts_file.write(f"{REDIRECT_IP} {website}\n")
                    print(f"Blocked website: {website}")
        except FileNotFoundError:
            print(f"Error: The file {HOSTS_PATH} was not found. Please create it.")
            # Optionally, create the file if it does not exist            

    def unblock_websites(self):
        """Unblock websites by removing their entries from the hosts file."""
        try:
            with open(HOSTS_PATH, 'r+') as hosts_file:
             lines = hosts_file.readlines()
             hosts_file.seek(0)
             hosts_file.truncate()
            for line in lines:
                if not any(website in line for website in self.blocked_websites):
                    hosts_file.write(line)
            print("Unblocked websites.")
        except FileNotFoundError:
            print(f"Error: The file {HOSTS_PATH} was not found. Please create it.")    

    def start_focus_session(self, blocked_websites):
        self.blocked_websites = blocked_websites
        self.tracking = True
        self.tracking_active = True
        self.block_websites()  # Block the websites at the start of the session
        
        # Start the blocking thread
        self.start_blocking_thread()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.end_focus_session)
        self.timer.start(60 * 1000)  # 1 minute interval

    def end_focus_session(self):
        self.tracking = False
        self.tracking_active = False
        self.timer.stop()
        self.unblock_websites()  # Unblock the websites when the session ends
        # Notify the user the session has ended
        QMessageBox.information(self, "Session Ended", "Your focus session has ended.")
    
    def start_blocking_thread(self):
        self.blocking_thread = threading.Thread(target=self.block_apps)
        self.blocking_thread.start()

    def stop_tracking(self):
        self.tracking_active = False
        if self.blocking_thread.is_alive():
            self.blocking_thread.join()

    def track_activity(self):
        # Tracking logic here
        active_window = get_active_window_title()

        # Example of managing memory: Clear old data from list
        if len(self.activity_log) > 1000:  # Arbitrary limit
            self.activity_log.pop(0)

        self.activity_log.append(active_window)
        self.save_to_db(active_window)
        
    def _track_activity_loop(self):
        while self.tracking_active:
            self.track_activity()
            time.sleep(5)  # Adjust the interval as necessary

    def start_tracking(self):
        self.tracking_active = True
        self.tracking_thread = threading.Thread(target=self._track_activity_loop)
        self.tracking_thread.start()

    def save_to_db(self, active_window):
        # Implement your database saving logic here
        conn = sqlite3.connect('activity_log.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_log (timestamp, window_title) VALUES (?, ?)",
                       (datetime.datetime.now(), active_window))
        conn.commit()
        conn.close()

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
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtWidgets import QWidget, QMessageBox
import time

# Path to the hosts file (might be different on Linux/Mac)
HOSTS_PATH = r'C:/Windows/System32/drivers/etc/hosts'
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

blocked_apps = ["SomeApp.exe", "AnotherApp.exe"]

class FocusTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tracking = False
        self.blocked_websites = []

    def block_apps(self):
        while self.tracking:
            try:
                current_time = datetime.datetime.now().time()
                focus_settings = get_focus_settings()
                if focus_settings:
                    start_time = datetime.datetime.strptime(focus_settings[0], "%H:%M").time()
                    end_time = datetime.datetime.strptime(focus_settings[1], "%H:%M").time()
                    blocked_apps = focus_settings[2].split(',')
                    blocked_websites = focus_settings[3].split(',')

                    if start_time <= current_time <= end_time:
                        active_title = get_active_window_title()
                        for app in blocked_apps:
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
        with open(HOSTS_PATH, 'r+') as hosts_file:
            content = hosts_file.read()
            for website in self.blocked_websites:
                if website not in content:
                    hosts_file.write(f"{REDIRECT_IP} {website}\n")
                    print(f"Blocked website: {website}")

    def unblock_websites(self):
        """Unblock websites by removing their entries from the hosts file."""
        with open(HOSTS_PATH, 'r+') as hosts_file:
            lines = hosts_file.readlines()
            hosts_file.seek(0)
            hosts_file.truncate()
            for line in lines:
                if not any(website in line for website in self.blocked_websites):
                    hosts_file.write(line)
            print("Unblocked websites.")

    def start_focus_session(self, blocked_websites):
        self.blocked_websites = blocked_websites
        self.tracking = True
        self.block_websites()  # Block the websites at the start of the session
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.end_focus_session)
        self.timer.start(60 * 1000)  # 1 minute interval

    def end_focus_session(self):
        self.tracking = False
        self.timer.stop()
        self.unblock_websites()  # Unblock the websites when the session ends
        # Notify the user the session has ended
        QMessageBox.information(self, "Session Ended", "Your focus session has ended.")

    def start_blocking_thread(self):
        self.blocking_thread = QThread()
        self.blocking_thread.run = self.block_apps
        self.blocking_thread.start()

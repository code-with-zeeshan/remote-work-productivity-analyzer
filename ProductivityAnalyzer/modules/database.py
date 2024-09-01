# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file contains  Handles all database interactions. for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

import sqlite3
from typing import Optional

def connect_db(db_name: str = 'activity_log.db') -> Optional[sqlite3.Connection]:
    """Connects to the SQLite database."""
    try:
        return sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table_if_not_exists(cursor: sqlite3.Cursor) -> None:
    """Creates the activity_log table if it doesn't exist."""
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                window_title TEXT
            )
        ''')
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def create_focus_settings_table(cursor: sqlite3.Cursor) -> None:
    """Creates the focus_settings table if it doesn't exist."""
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS focus_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                blocked_apps TEXT,
                blocked_websites TEXT
            )
        ''')
    except sqlite3.Error as e:
        print(f"Error creating focus settings table: {e}")

def save_focus_settings(conn: sqlite3.Connection, start_time: str, end_time: str, blocked_apps: str, blocked_websites: str) -> None:
    """Saves focus settings to the database."""
    try:
        cursor = conn.cursor()
        create_focus_settings_table(cursor)  # Ensure the table exists

        cursor.execute('''
            INSERT INTO focus_settings (start_time, end_time, blocked_apps, blocked_websites)
            VALUES (?, ?, ?, ?)
        ''', (start_time, end_time, blocked_apps, blocked_websites))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving focus settings: {e}")
 

def log_activity_to_db(conn: sqlite3.Connection, timestamp: str, window_title: str) -> None:
    """Logs activity to the database."""
    if not isinstance(timestamp, str) or not isinstance(window_title, str):
        raise ValueError("timestamp and window_title must be strings")
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (timestamp, window_title)
            VALUES (?, ?)
        ''', (timestamp, window_title))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging activity: {e}")
    

# Example usage:
if __name__ == "__main__":
    db_conn = connect_db()
    if db_conn:
        try:
            create_table_if_not_exists(db_conn.cursor())
            log_activity_to_db(db_conn, "2023-02-20 14:30:00", "Example Window Title")
        finally:
            db_conn.close()

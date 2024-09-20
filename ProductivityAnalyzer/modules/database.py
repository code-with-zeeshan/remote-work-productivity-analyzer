# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file handles all database interactions for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

import psycopg2
from psycopg2.pool import SimpleConnectionPool  # Import SimpleConnectionPool directly

class Database:
    def __init__(self):
        self.pool = None
        self.create_connection_pool()

    def create_connection_pool(self):
        """Create a connection pool to the database"""
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            user='postgres',
            password='zeeshan321##',
            host='localhost',
            port='5432',
            database='remotework'
        )
        try:
            print("Connection pool created successfully")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error while connecting to PostgreSQL: {error}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            raise Exception("Connection pool not created")
        self.connection = self.pool.getconn()
        if self.connection:
            print("Connection obtained successfully")
        return self.connection
        
    def log_activity(self, timestamp, activity):
        """Log the activity into the database"""
        try:
            if self.connection is None:  # This is where the error occurred
                print("No active database connection.")
                return

        
            cursor = self.connection.cursor()
            insert_query = """
                INSERT INTO activity_logs (timestamp, activity)
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (timestamp, activity))
            self.connection.commit()
            cursor.close()
            print(f"Activity logged: {activity}")
        except Exception as e:
            print(f"Error logging activity: {e}")
            if self.connection:
               self.connection.rollback()  # Rollback the transaction if there was an error

    def close_connection(self, conn):
        try:
            if conn and self.pool is not None:
                self.pool.putconn(conn)
            elif self.pool is None:
                print("Connection pool is not initialized.")
        except Exception as e:
            print(f"Error while closing connection: {e}")

    def close_all_connections(self):
        if self.pool:
            self.pool.closeall()

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if conn is None:
            print("Failed to get a database connection")
            return  # Exit the function if no connection could be obtained

        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
        except Exception as e:
            print(f"Database query error: {e}")
            if conn is not None:
                conn.rollback()
        finally:
            if conn is not None:
                self.close_connection(conn)


    def create_activity_log_table(self, cursor) -> None:
        """Creates the activity_log table if it doesn't exist."""
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    window_title TEXT
                )
            ''')
        except psycopg2.Error as e:
            print(f"Error creating activity_log table: {e}")

    def create_focus_settings_table(self, cursor) -> None:
        """Creates the focus_settings table if it doesn't exist."""
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS focus_settings (
                    id SERIAL PRIMARY KEY,
                    start_time TIME,
                    end_time TIME,
                    blocked_apps TEXT,
                    blocked_websites TEXT
                )
            ''')
        except psycopg2.Error as e:
            print(f"Error creating focus_settings table: {e}")

    def create_index(self, cursor) -> None:
        """Creates an index on the timestamp column in activity_log."""
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
            ''')
        except psycopg2.Error as e:
            print(f"Error creating index: {e}")

    def save_focus_settings(self, start_time, end_time, blocked_apps, blocked_websites):
        conn = self.get_connection()
        if conn is None:
            print("Failed to get a database connection")
            return  # Exit the function if no connection could be obtained

        try:
            cursor = conn.cursor()
            cursor.execute('''
                   INSERT INTO focus_settings ( start_time, end_time, blocked_apps, blocked_websites)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id) DO UPDATE
                   SET start_time = EXCLUDED.start_time,
                   end_time = EXCLUDED.end_time,
                   blocked_apps = EXCLUDED.blocked_apps,
                   blocked_websites = EXCLUDED.blocked_websites
                   ''', (start_time, end_time, ','.join(blocked_apps), ','.join(blocked_websites)))

            conn.commit()
        finally:
            cursor.close()
            self.close_connection(conn)

    def log_activity_to_db(self, timestamp: str, window_title: str) -> None:
        """Logs activity to the database."""
        conn = self.get_connection()
        if conn is None:
            print("Failed to get a database connection")
            return  # Exit the function if no connection could be obtained

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_log (timestamp, window_title)
                VALUES (%s, %s)
            ''', (timestamp, window_title))
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error logging activity: {e}")
        finally:
            cursor.close()
            self.close_connection(conn)

    def create_table_if_not_exists(self):
        conn = self.get_connection()  # Changed from self.connect() to self.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    window_title TEXT
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()

    

# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file is the main content for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------

# main.py
import sys

from PyQt5.QtWidgets import QApplication
from modules.ui import ProductivityAnalyzerApp
from modules.ui import ProductivityAnalyzerHome
from modules.database import Database  # Adjust import according to your structure
from modules.tracker import FocusTrackerApp  # Adjust import according to your structure


def main():
    app = QApplication(sys.argv)
    
    db = None
    try:
        # Initialize database and tracker
        db = Database()
         # Example usage:
        conn = db.get_connection()
        if conn:
            print("Connection obtained successfully")
            # Your application logic here
            db.close_connection(conn)

        tracker = FocusTrackerApp()
        
        # Create the UI
        analyzer = ProductivityAnalyzerApp()
        
       
        
        # Show the UI
        analyzer.show()
        
        # Start tracking
        tracker.start_tracking()
        
        # Run the application
        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(f"Error executing application: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        if db:
            db.close_all_connections()  # Correct method to close the database connection

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProductivityAnalyzerHome()
    window.show()
    sys.exit(app.exec_())

  

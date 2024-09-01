# ----------------------------------------------------------------------------
# Project Name: Remote Work Productivity Analyzer
# Author: Mohammad Zeesahn
# Email: zeeshansayfyebusiness@gmail.com
# License: MIT License
# Description: This file is the main content  for the Remote 
# Work Productivity Analyzer application.
# ----------------------------------------------------------------------------


# main.py
import sys
import os 
from PyQt5.QtWidgets import QApplication
from modules.ui import ProductivityAnalyzerApp

# Add the parent directory of 'modules' to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Create and show the main application window
    try:
        analyzer = ProductivityAnalyzerApp()
        analyzer.show()
    except Exception as e:
        print(f"Error creating ProductivityAnalyzerApp: {e}")
        sys.exit(1)

    # Execute the application
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error executing application: {e}")
        sys.exit(1)

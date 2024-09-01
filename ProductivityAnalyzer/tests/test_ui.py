import unittest
from PyQt5.QtWidgets import QApplication
from modules.ui import ProductivityAnalyzerApp

class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def test_export_report(self):
        # This is a simplified example; you'd want to test the actual functionality
        app = ProductivityAnalyzerApp()
        app.export_report()  # Ensure no exceptions are raised

if __name__ == '__main__':
    unittest.main()

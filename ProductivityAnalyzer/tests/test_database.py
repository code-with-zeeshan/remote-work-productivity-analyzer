import unittest
import sqlite3
from modules.database import connect_db, create_table_if_not_exists, log_activity_to_db

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')  # In-memory database for testing
        self.cursor = self.conn.cursor()
        create_table_if_not_exists(self.cursor)

    def test_log_activity_to_db(self):
        log_activity_to_db(self.cursor, '2024-08-31 10:00:00', 'Test Window')
        self.cursor.execute('SELECT * FROM activity_log')
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], '2024-08-31 10:00:00')
        self.assertEqual(rows[0][2], 'Test Window')

    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()

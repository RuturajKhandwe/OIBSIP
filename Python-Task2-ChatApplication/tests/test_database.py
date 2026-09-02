import os
import unittest
import sqlite3
from app import create_app
from database.db import get_db, init_db, close_db

class TestDatabase(unittest.TestCase):
    """Test suite for SQLite schema creation, constraints, and connection pooling."""

    def setUp(self):
        self.app = create_app('testing')
        self.db_path = self.app.config['DATABASE_PATH']
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

    def tearDown(self):
        close_db()
        self.app_context.pop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_default_schema_tables_exist(self):
        """Verify users, rooms, messages, room_members tables exist."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row['name'] for row in cursor.fetchall()}
        
        self.assertIn('users', tables)
        self.assertIn('rooms', tables)
        self.assertIn('messages', tables)
        self.assertIn('room_members', tables)

    def test_default_general_room_seeded(self):
        """Verify default 'General' chat room is created on init."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM rooms WHERE name = 'General'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['name'], 'General')

    def test_foreign_key_constraint_enforced(self):
        """Verify foreign key constraints prevent inserting messages for non-existent room."""
        db = get_db()
        cursor = db.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO messages (room_id, user_id, content) VALUES (999, 1, 'Test message')"
            )

if __name__ == '__main__':
    unittest.main()

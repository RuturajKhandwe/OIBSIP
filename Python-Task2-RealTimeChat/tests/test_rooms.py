import os
import unittest
from app import create_app
from database.db import init_db, close_db
from auth.service import AuthService
from chat.rooms import RoomManager

class TestRoomManager(unittest.TestCase):
    """Test suite for room creation, room listing, and active presence tracking."""

    def setUp(self):
        self.app = create_app('testing')
        self.db_path = self.app.config['DATABASE_PATH']
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

        # Create test user
        _, _, self.user = AuthService.register_user('roomcreator', 'password123', 'password123')

    def tearDown(self):
        close_db()
        self.app_context.pop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_create_room_success(self):
        """Test creating a new chat room."""
        success, msg, room = RoomManager.create_room('DevOps', self.user.id)
        self.assertTrue(success, f"Room creation failed: {msg}")
        self.assertIsNotNone(room)
        self.assertEqual(room['name'], 'DevOps')

    def test_duplicate_room_rejection(self):
        """Test creating a room with duplicate name is rejected."""
        RoomManager.create_room('Python', self.user.id)
        success, msg, _ = RoomManager.create_room('Python', self.user.id)
        self.assertFalse(success)
        self.assertIn('already exists', msg)

    def test_presence_tracking(self):
        """Test in-memory socket presence tracking."""
        RoomManager.add_user_presence('sid123', 'alice', 'General')
        online = RoomManager.get_online_users('General')
        self.assertIn('alice', online)

        RoomManager.remove_user_presence('sid123')
        online_after = RoomManager.get_online_users('General')
        self.assertNotIn('alice', online_after)

if __name__ == '__main__':
    unittest.main()

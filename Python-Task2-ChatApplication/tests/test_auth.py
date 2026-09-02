import os
import unittest
from pathlib import Path
from app import create_app
from database.db import init_db, close_db
from auth.service import AuthService
from werkzeug.security import check_password_hash

class TestAuthService(unittest.TestCase):
    """Test suite for authentication service, password hashing, and user registration."""

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

    def test_user_registration_success(self):
        """Test successful registration with password hashing."""
        success, msg, user = AuthService.register_user('alice', 'securepass123', 'securepass123')
        self.assertTrue(success, f"Registration failed: {msg}")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'alice')
        self.assertTrue(check_password_hash(user.password_hash, 'securepass123'))

    def test_duplicate_username_rejection(self):
        """Test duplicate username registration rejection."""
        AuthService.register_user('bob', 'password123', 'password123')
        success, msg, user = AuthService.register_user('bob', 'password456', 'password456')
        self.assertFalse(success)
        self.assertIn('taken', msg.lower())

    def test_invalid_username_validation(self):
        """Test username boundary and character validation."""
        success, msg, _ = AuthService.register_user('ab', 'password123', 'password123')
        self.assertFalse(success)

        success, msg, _ = AuthService.register_user('user@name', 'password123', 'password123')
        self.assertFalse(success)

    def test_password_mismatch_rejection(self):
        """Test password mismatch handling."""
        success, msg, _ = AuthService.register_user('charlie', 'password123', 'differentpass')
        self.assertFalse(success)
        self.assertIn('do not match', msg.lower())

    def test_user_authentication_success(self):
        """Test valid user authentication."""
        AuthService.register_user('dave', 'mysecretpass', 'mysecretpass')
        success, msg, user = AuthService.authenticate_user('dave', 'mysecretpass')
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'dave')

    def test_user_authentication_failure(self):
        """Test invalid credentials authentication failure."""
        AuthService.register_user('eve', 'mysecretpass', 'mysecretpass')
        success, msg, user = AuthService.authenticate_user('eve', 'wrongpassword')
        self.assertFalse(success)
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()

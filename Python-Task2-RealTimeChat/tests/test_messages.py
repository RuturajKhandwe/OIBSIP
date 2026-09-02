import os
import unittest
from app import create_app
from database.db import init_db, close_db
from auth.service import AuthService
from chat.service import ChatService
from utils.security import sanitize_html
from utils.emoji import parse_emoji_shortcodes

class TestMessages(unittest.TestCase):
    """Test suite for message validation, security sanitization, emoji parsing, and history pagination."""

    def setUp(self):
        self.app = create_app('testing')
        self.db_path = self.app.config['DATABASE_PATH']
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

        # Create test user
        _, _, self.user = AuthService.register_user('sender1', 'password123', 'password123')

    def tearDown(self):
        close_db()
        self.app_context.pop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_html_sanitization_prevents_xss(self):
        """Verify HTML script tags are escaped safely."""
        raw_xss = "<script>alert('hack')</script>"
        clean = sanitize_html(raw_xss)
        self.assertNotIn('<script>', clean)
        self.assertIn('&lt;script&gt;', clean)

    def test_emoji_shortcode_parsing(self):
        """Verify shortcodes are replaced while preserving non-emoji text."""
        text = "Hello world :) :heart: :fire:"
        parsed = parse_emoji_shortcodes(text)
        self.assertEqual(parsed, "Hello world 🙂 ❤️ 🔥")

    def test_empty_message_rejection(self):
        """Verify empty or whitespace-only messages are rejected."""
        success, msg, _ = ChatService.save_message(self.user.id, 'General', '   ')
        self.assertFalse(success)

    def test_message_save_and_history_retrieval(self):
        """Verify messages persist to SQLite and retrieve in chronological order."""
        ChatService.save_message(self.user.id, 'General', 'First message')
        ChatService.save_message(self.user.id, 'General', 'Second message')

        history = ChatService.get_room_history('General', limit=50)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['content'], 'First message')
        self.assertEqual(history[1]['content'], 'Second message')

if __name__ == '__main__':
    unittest.main()

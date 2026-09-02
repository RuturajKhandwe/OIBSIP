import os
import unittest
from app import create_app, socketio
from database.db import init_db, close_db
from auth.service import AuthService

class TestSocketEvents(unittest.TestCase):
    """Test suite for Flask-SocketIO event handlers using Socket.IO test client."""

    def setUp(self):
        self.app = create_app('testing')
        self.db_path = self.app.config['DATABASE_PATH']
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

        # Register test user
        _, _, self.user = AuthService.register_user('socketuser', 'password123', 'password123')

    def tearDown(self):
        close_db()
        self.app_context.pop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_unauthenticated_socket_connection_rejected(self):
        """Verify unauthenticated socket connection is disconnected."""
        client = socketio.test_client(self.app)
        self.assertFalse(client.is_connected())

    def test_authenticated_socket_flow(self):
        """Verify authenticated socket client connection, room join, and message emit."""
        # Establish authenticated session client
        with self.app.test_client() as flask_client:
            flask_client.post('/auth/login', data={
                'username': 'socketuser',
                'password': 'password123'
            })

            # Create SocketIO test client attached to Flask session context
            client = socketio.test_client(self.app, flask_test_client=flask_client)
            self.assertTrue(client.is_connected())

            # Join room 'General'
            client.emit('join_room', {'room_name': 'General'})
            received = client.get_received()
            
            # Should receive room history and presence update
            event_names = [e['name'] for e in received]
            self.assertIn('message_history', event_names)
            self.assertIn('presence_update', event_names)

            # Send chat message
            client.emit('send_message', {'room_name': 'General', 'content': 'Hello WebSocket! :)'})
            msg_received = client.get_received()
            
            msg_events = [e['name'] for e in msg_received if e['name'] == 'receive_message']
            self.assertTrue(len(msg_events) > 0)

            client.disconnect()

if __name__ == '__main__':
    unittest.main()

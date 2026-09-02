import logging
from flask import session, request
from flask_socketio import emit, join_room, leave_room, disconnect
from chat.rooms import RoomManager
from chat.service import ChatService
from utils.security import is_authenticated, get_current_user_id, get_current_username

logger = logging.getLogger(__name__)

def register_socket_events(socketio):
    """Registers Flask-SocketIO event handlers with the server instance."""

    @socketio.on('connect')
    def handle_connect():
        """Authenticates client connection against session."""
        if not is_authenticated():
            logger.warning(f"Unauthorized socket connection attempt from SID: {request.sid}")
            emit('error', {'message': 'Authentication required. Please log in.'})
            disconnect()
            return False
        
        username = get_current_username()
        logger.info(f"Socket connected: Username '{username}' (SID: {request.sid})")
        emit('connection_status', {'status': 'connected', 'username': username})
        
        # Send initial room list
        rooms = RoomManager.get_all_rooms()
        emit('room_list', rooms)

    @socketio.on('disconnect')
    def handle_disconnect():
        """Cleans up user active presence upon socket disconnect."""
        sid = request.sid
        presence_info = RoomManager.remove_user_presence(sid)
        if presence_info:
            username, room_name = presence_info
            logger.info(f"Socket disconnected: Username '{username}' from Room '{room_name}' (SID: {sid})")
            
            # Broadcast user left system message to room
            emit('system_message', {
                'room_name': room_name,
                'content': f"{username} has left the chat.",
                'type': 'leave'
            }, room=room_name)

            # Broadcast updated online presence
            online_users = RoomManager.get_online_users(room_name)
            emit('presence_update', {
                'room_name': room_name,
                'online_users': online_users,
                'count': len(online_users)
            }, room=room_name)

    @socketio.on('get_rooms')
    def handle_get_rooms():
        """Returns current room listing."""
        if not is_authenticated():
            return
        rooms = RoomManager.get_all_rooms()
        emit('room_list', rooms)

    @socketio.on('create_room')
    def handle_create_room(data):
        """Handles new room creation requests."""
        if not is_authenticated():
            emit('error', {'message': 'Unauthorized action.'})
            return

        user_id = get_current_user_id()
        room_name = data.get('room_name', '') if isinstance(data, dict) else ''

        success, message, room_dict = RoomManager.create_room(room_name, user_id)
        if not success:
            emit('error', {'message': message})
            return

        logger.info(f"Room created: '{room_name}' by User ID {user_id}")
        
        # Broadcast updated room list to all connected clients
        rooms = RoomManager.get_all_rooms()
        emit('room_list', rooms, broadcast=True)
        emit('room_created_success', {'room': room_dict})

    @socketio.on('join_room')
    def handle_join_room(data):
        """Handles room join requests, history retrieval, and presence broadcast."""
        if not is_authenticated():
            emit('error', {'message': 'Unauthorized action.'})
            return

        username = get_current_username()
        room_name = data.get('room_name', '') if isinstance(data, dict) else ''
        room_name = room_name.strip()

        room = RoomManager.get_room_by_name(room_name)
        if not room:
            emit('error', {'message': f"Room '{room_name}' does not exist."})
            return

        sid = request.sid

        # Remove from previous room session if active
        prev_info = RoomManager.remove_user_presence(sid)
        if prev_info:
            prev_user, prev_room = prev_info
            leave_room(prev_room)
            online_prev = RoomManager.get_online_users(prev_room)
            emit('presence_update', {
                'room_name': prev_room,
                'online_users': online_prev,
                'count': len(online_prev)
            }, room=prev_room)

        # Join new Socket.IO channel
        join_room(room_name)
        RoomManager.add_user_presence(sid, username, room_name)

        logger.info(f"User '{username}' joined room '{room_name}' (SID: {sid})")

        # Fetch chronological 50 message history
        history = ChatService.get_room_history(room_name, limit=50)
        emit('message_history', {
            'room_name': room_name,
            'messages': history
        })

        # Broadcast user_joined notification to room members
        emit('system_message', {
            'room_name': room_name,
            'content': f"{username} has joined the room.",
            'type': 'join'
        }, room=room_name)

        # Broadcast updated presence roster
        online_users = RoomManager.get_online_users(room_name)
        emit('presence_update', {
            'room_name': room_name,
            'online_users': online_users,
            'count': len(online_users)
        }, room=room_name)

    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handles room leave requests."""
        if not is_authenticated():
            return

        username = get_current_username()
        room_name = data.get('room_name', '') if isinstance(data, dict) else ''
        sid = request.sid

        leave_room(room_name)
        RoomManager.remove_user_presence(sid)

        emit('system_message', {
            'room_name': room_name,
            'content': f"{username} has left the room.",
            'type': 'leave'
        }, room=room_name)

        online_users = RoomManager.get_online_users(room_name)
        emit('presence_update', {
            'room_name': room_name,
            'online_users': online_users,
            'count': len(online_users)
        }, room=room_name)

    @socketio.on('send_message')
    def handle_send_message(data):
        """Validates, persists, and broadcasts chat message to room."""
        if not is_authenticated():
            emit('error', {'message': 'Unauthorized action.'})
            return

        if not isinstance(data, dict):
            emit('error', {'message': 'Invalid payload format.'})
            return

        user_id = get_current_user_id()
        room_name = data.get('room_name', '').strip()
        content = data.get('content', '')

        success, message, msg_dict = ChatService.save_message(user_id, room_name, content)
        if not success:
            emit('error', {'message': message})
            return

        # Broadcast receive_message event to target room
        emit('receive_message', msg_dict, room=room_name)

import sqlite3
from typing import List, Dict, Set, Tuple, Optional
from database.db import get_db
from models.room import Room
from utils.validators import validate_room_name

class RoomManager:
    """Manages chat rooms and tracks real-time active user presence per room."""
    
    # In-memory mapping of room_name -> Set[username]
    _active_presence: Dict[str, Set[str]] = {}
    # In-memory mapping of socket_id -> (username, room_name)
    _socket_sessions: Dict[str, Tuple[str, str]] = {}

    @classmethod
    def get_all_rooms(cls) -> List[dict]:
        """Retrieves list of all available rooms from database."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.id, r.name, r.created_by, r.created_at, u.username as creator_username
            FROM rooms r
            JOIN users u ON r.created_by = u.id
            ORDER BY r.name ASC
            """
        )
        rows = cursor.fetchall()
        rooms = []
        for r in rows:
            room_obj = Room.from_row(r)
            room_dict = room_obj.to_dict() if room_obj else {}
            room_dict['online_count'] = len(cls._active_presence.get(r['name'], set()))
            rooms.append(room_dict)
        return rooms

    @classmethod
    def get_room_by_name(cls, room_name: str) -> Optional[Room]:
        """Fetches room object by name."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.id, r.name, r.created_by, r.created_at, u.username as creator_username
            FROM rooms r
            JOIN users u ON r.created_by = u.id
            WHERE r.name = ?
            """,
            (room_name.strip(),)
        )
        row = cursor.fetchone()
        return Room.from_row(row) if row else None

    @classmethod
    def create_room(cls, room_name: str, created_by_user_id: int) -> Tuple[bool, str, Optional[dict]]:
        """Creates a new room in database if name is valid and unique."""
        valid, msg = validate_room_name(room_name)
        if not valid:
            return False, msg, None

        room_name = room_name.strip()
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
            if cursor.fetchone():
                return False, f"Room '{room_name}' already exists.", None

            cursor.execute(
                "INSERT INTO rooms (name, created_by) VALUES (?, ?)",
                (room_name, created_by_user_id)
            )
            db.commit()
            room_id = cursor.lastrowid
            
            room = cls.get_room_by_name(room_name)
            room_dict = room.to_dict() if room else {'id': room_id, 'name': room_name}
            room_dict['online_count'] = 0
            return True, "Room created successfully!", room_dict

        except sqlite3.Error as e:
            db.rollback()
            return False, f"Database error creating room: {str(e)}", None

    @classmethod
    def add_user_presence(cls, sid: str, username: str, room_name: str):
        """Registers user active socket presence in a room."""
        if room_name not in cls._active_presence:
            cls._active_presence[room_name] = set()
        cls._active_presence[room_name].add(username)
        cls._socket_sessions[sid] = (username, room_name)

    @classmethod
    def remove_user_presence(cls, sid: str) -> Optional[Tuple[str, str]]:
        """Removes socket presence and returns (username, room_name) if found."""
        if sid in cls._socket_sessions:
            username, room_name = cls._socket_sessions.pop(sid)
            if room_name in cls._active_presence:
                cls._active_presence[room_name].discard(username)
                if not cls._active_presence[room_name]:
                    del cls._active_presence[room_name]
            return username, room_name
        return None

    @classmethod
    def get_online_users(cls, room_name: str) -> List[str]:
        """Returns sorted list of active usernames in a room."""
        return sorted(list(cls._active_presence.get(room_name, set())))

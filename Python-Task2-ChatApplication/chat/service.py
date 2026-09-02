import sqlite3
from typing import List, Tuple, Optional
from database.db import get_db
from models.message import Message
from utils.validators import validate_message_content
from utils.security import sanitize_html
from utils.emoji import parse_emoji_shortcodes

class ChatService:
    """Service class managing chat message processing, persistence, and history loading."""

    @staticmethod
    def save_message(user_id: int, room_name: str, raw_content: str) -> Tuple[bool, str, Optional[dict]]:
        """Validates, sanitizes, parses emoji shortcodes, and saves message to SQLite database."""
        valid, msg = validate_message_content(raw_content)
        if not valid:
            return False, msg, None

        # Sanitize HTML to prevent XSS
        clean_content = sanitize_html(raw_content)

        # Translate emoji shortcodes (e.g., :) -> 🙂)
        final_content = parse_emoji_shortcodes(clean_content)

        db = get_db()
        cursor = db.cursor()

        try:
            # Get room ID
            cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name.strip(),))
            room_row = cursor.fetchone()
            if not room_row:
                return False, f"Target room '{room_name}' does not exist.", None
            
            room_id = room_row['id']

            # Insert message
            cursor.execute(
                "INSERT INTO messages (room_id, user_id, content) VALUES (?, ?, ?)",
                (room_id, user_id, final_content)
            )
            db.commit()
            message_id = cursor.lastrowid

            # Fetch inserted message with join to user table
            cursor.execute(
                """
                SELECT m.id, m.room_id, m.user_id, m.content, m.timestamp, u.username as sender, r.name as room_name
                FROM messages m
                JOIN users u ON m.user_id = u.id
                JOIN rooms r ON m.room_id = r.id
                WHERE m.id = ?
                """,
                (message_id,)
            )
            msg_row = cursor.fetchone()
            msg_obj = Message.from_row(msg_row)
            return True, "Message saved.", msg_obj.to_dict() if msg_obj else None

        except sqlite3.Error as e:
            db.rollback()
            return False, f"Database error saving message: {str(e)}", None

    @staticmethod
    def get_room_history(room_name: str, limit: int = 50) -> List[dict]:
        """Fetches up to `limit` recent messages for a room ordered chronologically."""
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT * FROM (
                SELECT m.id, m.room_id, m.user_id, m.content, m.timestamp, u.username as sender, r.name as room_name
                FROM messages m
                JOIN users u ON m.user_id = u.id
                JOIN rooms r ON m.room_id = r.id
                WHERE r.name = ?
                ORDER BY m.timestamp DESC, m.id DESC
                LIMIT ?
            ) ORDER BY timestamp ASC, id ASC
            """,
            (room_name.strip(), limit)
        )
        rows = cursor.fetchall()
        history = []
        for r in rows:
            msg_obj = Message.from_row(r)
            if msg_obj:
                history.append(msg_obj.to_dict())
        return history

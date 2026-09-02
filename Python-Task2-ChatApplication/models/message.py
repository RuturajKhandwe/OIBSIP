from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    """Domain model representing a chat message."""
    id: int
    room_id: int
    user_id: int
    content: str
    timestamp: Optional[str] = None
    sender_username: Optional[str] = None
    room_name: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializes message domain object for WebSocket payload."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'sender': self.sender_username or 'Unknown',
            'room_name': self.room_name,
            'content': self.content,
            'timestamp': str(self.timestamp) if self.timestamp else None
        }

    @classmethod
    def from_row(cls, row) -> Optional['Message']:
        """Instantiates Message object from SQLite Row."""
        if not row:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            room_id=row['room_id'],
            user_id=row['user_id'],
            content=row['content'],
            timestamp=row['timestamp'] if 'timestamp' in keys else None,
            sender_username=row['sender'] if 'sender' in keys else (row['username'] if 'username' in keys else None),
            room_name=row['room_name'] if 'room_name' in keys else None
        )

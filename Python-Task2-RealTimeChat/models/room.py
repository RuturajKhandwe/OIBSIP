from dataclasses import dataclass
from typing import Optional

@dataclass
class Room:
    """Domain model representing a chat room."""
    id: int
    name: str
    created_by: int
    created_at: Optional[str] = None
    creator_username: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializes room domain object."""
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': str(self.created_at) if self.created_at else None,
            'creator_username': self.creator_username
        }

    @classmethod
    def from_row(cls, row) -> Optional['Room']:
        """Instantiates Room object from SQLite Row."""
        if not row:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            name=row['name'],
            created_by=row['created_by'],
            created_at=row['created_at'] if 'created_at' in keys else None,
            creator_username=row['creator_username'] if 'creator_username' in keys else None
        )

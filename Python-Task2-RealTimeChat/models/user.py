from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Domain model representing a registered user."""
    id: int
    username: str
    password_hash: str
    created_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializes user domain object (excluding sensitive password hash)."""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def from_row(cls, row) -> Optional['User']:
        """Instantiates User object from SQLite Row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=row['created_at'] if 'created_at' in row.keys() else None
        )

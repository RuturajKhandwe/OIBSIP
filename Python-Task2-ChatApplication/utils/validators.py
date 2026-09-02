import re
from typing import Tuple

def validate_username(username: str, min_len: int = 3, max_len: int = 30) -> Tuple[bool, str]:
    """Validates username formatting rules."""
    if not username or not isinstance(username, str):
        return False, "Username is required."
    
    username = username.strip()
    if len(username) < min_len or len(username) > max_len:
        return False, f"Username must be between {min_len} and {max_len} characters."
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores."
    
    return True, ""

def validate_password(password: str, min_len: int = 6) -> Tuple[bool, str]:
    """Validates password length rules."""
    if not password or not isinstance(password, str):
        return False, "Password is required."
    
    if len(password) < min_len:
        return False, f"Password must be at least {min_len} characters long."
    
    return True, ""

def validate_room_name(room_name: str, min_len: int = 3, max_len: int = 30) -> Tuple[bool, str]:
    """Validates chat room name formatting rules."""
    if not room_name or not isinstance(room_name, str):
        return False, "Room name is required."
    
    room_name = room_name.strip()
    if len(room_name) < min_len or len(room_name) > max_len:
        return False, f"Room name must be between {min_len} and {max_len} characters."
    
    if not re.match(r'^[a-zA-Z0-9_\-\s]+$', room_name):
        return False, "Room name can only contain letters, numbers, spaces, hyphens, and underscores."
    
    return True, ""

def validate_message_content(content: str, max_len: int = 1000) -> Tuple[bool, str]:
    """Validates message length and content rules."""
    if not content or not isinstance(content, str):
        return False, "Message content cannot be empty."
    
    content = content.strip()
    if len(content) == 0:
        return False, "Message content cannot be blank."
    
    if len(content) > max_len:
        return False, f"Message content cannot exceed {max_len} characters."
    
    return True, ""

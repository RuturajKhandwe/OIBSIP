import html
from flask import session

def sanitize_html(text: str) -> str:
    """Escapes HTML special characters in user input to prevent XSS attacks."""
    if not text:
        return ""
    return html.escape(text.strip(), quote=True)

def is_authenticated() -> bool:
    """Checks whether the current session contains an authenticated user."""
    return 'user_id' in session and 'username' in session

def get_current_user_id() -> int:
    """Returns current user ID from session or None."""
    return session.get('user_id')

def get_current_username() -> str:
    """Returns current username from session or None."""
    return session.get('username')

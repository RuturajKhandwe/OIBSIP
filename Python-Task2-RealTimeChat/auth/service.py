import sqlite3
from typing import Tuple, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from models.user import User
from utils.validators import validate_username, validate_password

class AuthService:
    """Service class encapsulating user authentication and credential management."""

    @staticmethod
    def register_user(username: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[User]]:
        """Registers a new user with password hashing and username uniqueness checks."""
        # Validate username
        valid_u, msg_u = validate_username(username)
        if not valid_u:
            return False, msg_u, None

        # Validate password
        valid_p, msg_p = validate_password(password)
        if not valid_p:
            return False, msg_p, None

        # Check confirmation match
        if password != confirm_password:
            return False, "Passwords do not match.", None

        username = username.strip()
        db = get_db()
        cursor = db.cursor()

        try:
            # Check duplicate username
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "Username is already taken. Please choose another.", None

            # Hash password
            pw_hash = generate_password_hash(password)

            # Insert user record
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, pw_hash)
            )
            db.commit()

            user_id = cursor.lastrowid
            user = User(id=user_id, username=username, password_hash=pw_hash)
            return True, "Registration successful!", user

        except sqlite3.Error as e:
            db.rollback()
            return False, f"Database error during registration: {str(e)}", None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Authenticates user credentials against Werkzeug password hash."""
        if not username or not password:
            return False, "Username and password are required.", None

        username = username.strip()
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if not row:
            return False, "Invalid username or password.", None

        user = User.from_row(row)
        if not check_password_hash(user.password_hash, password):
            return False, "Invalid username or password.", None

        return True, "Authentication successful!", user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Retrieves a user object by ID."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE id = ?", (user_id,))
        return User.from_row(cursor.fetchone())

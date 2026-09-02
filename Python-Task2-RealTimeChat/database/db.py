import sqlite3
import os
from pathlib import Path
from flask import current_app, g

def get_db_connection(db_path=None):
    """Establishes and returns a connection to the SQLite database."""
    if db_path is None:
        db_path = current_app.config['DATABASE_PATH']
    
    # Ensure directory exists for database file if it's a file path
    if db_path != ':memory:':
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Enable foreign keys and Write-Ahead Logging for concurrency
    conn.execute("PRAGMA foreign_keys = ON;")
    if db_path != ':memory:':
        conn.execute("PRAGMA journal_mode = WAL;")
        
    return conn

def get_db():
    """Gets the database connection for the current application context."""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None, db_path=None):
    """Initializes the database schema and seeds default data."""
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    if app:
        with app.app_context():
            conn = get_db()
            conn.executescript(schema_sql)
            _seed_default_data(conn)
            conn.commit()
    else:
        conn = get_db_connection(db_path)
        try:
            conn.executescript(schema_sql)
            _seed_default_data(conn)
            conn.commit()
        finally:
            conn.close()

def _seed_default_data(conn):
    """Seeds the initial System user and default 'General' chat room if not present."""
    cursor = conn.cursor()
    
    # Seed System User (id=1)
    cursor.execute("SELECT id FROM users WHERE username = ?", ('System',))
    system_user = cursor.fetchone()
    if not system_user:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ('System', 'SYSTEM_ACCOUNT_NO_LOGIN')
        )
        system_user_id = cursor.lastrowid
    else:
        system_user_id = system_user['id']

    # Seed Default General Room
    cursor.execute("SELECT id FROM rooms WHERE name = ?", ('General',))
    general_room = cursor.fetchone()
    if not general_room:
        cursor.execute(
            "INSERT INTO rooms (name, created_by) VALUES (?, ?)",
            ('General', system_user_id)
        )

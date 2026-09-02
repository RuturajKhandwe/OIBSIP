# Real-Time Multi-Room Chat Application

> A production-grade, real-time messaging application built with Python, Flask, Flask-SocketIO, SQLite3, and Vanilla ES6 JavaScript. Designed for high usability, clean modular architecture, security, and portfolio readiness.

---

## 📋 Executive Overview

The **Real-Time Multi-Room Chat Application** is an industry-level real-time messaging platform targeting the **Advanced Tier** requirements of full-stack Python software engineering. It provides bidirectional communication via WebSockets/Socket.IO, session-authenticated multi-room chat management, persistent message storage in SQLite, live online presence tracking, browser desktop notifications, and shortcode emoji translation inside a sleek glassmorphic dark-mode web GUI.

---

## 🌟 Feature Breakdown

### 🟢 Beginner Tier Baseline (100% Implemented)
- [x] **Server Listener**: Multi-client Flask-SocketIO backend listening on `127.0.0.1:5000`.
- [x] **Client Connection**: Web client establishing real-time Socket.IO WebSocket connections.
- [x] **Bidirectional Messaging**: Messages transmitted and displayed instantly without page refreshes.
- [x] **ISO Timestamps**: All messages display formatted timestamps (`[14:35] Alice: Hello`).
- [x] **Graceful Disconnects**: Automatic cleanup of socket session context upon tab closure or network drops.
- [x] **Localhost Execution**: Zero external server dependencies; fully runnable locally on Windows/Linux/macOS.

### 🚀 Advanced Tier Features (100% Implemented)
- [x] **Modern Dark GUI**: Responsive CSS3 glassmorphism UI with Google Font ('Inter') and active room feeds.
- [x] **Secure Authentication**: User registration, login, logout, and Werkzeug `scrypt`/`pbkdf2` password hashing.
- [x] **Multiple Chat Rooms**: Dynamic room creation, listing, switching, and room-isolated broadcasting.
- [x] **SQLite Message History**: Persistent SQLite message storage with automatic loading of the 50 most recent messages upon joining a room.
- [x] **Real-Time Presence Tracking**: In-memory socket session tracker displaying active online members per room.
- [x] **Desktop Notifications**: HTML5 Browser Notification API triggers when chat window is unfocused or hidden.
- [x] **Emoji Shortcodes**: Custom parser translating shortcodes (e.g. `:)` -> `🙂`, `:heart:` -> `❤️`) without altering standard text.
- [x] **Security Sanitization**: Parameterized SQL queries preventing SQL injection and server-side HTML escaping preventing XSS.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Core** | Python 3.10+ | Primary server-side programming language |
| **Web Framework** | Flask 3.1+ | WSGI routing, session management, and blueprint application factory |
| **Real-time Engine**| Flask-SocketIO 5.6+ | WebSocket and HTTP long-polling event handling |
| **Database** | SQLite3 | Relational file-based database for users, rooms, and messages |
| **Authentication**| Werkzeug `security` | Industrial password hashing (`generate_password_hash`, `check_password_hash`) |
| **Frontend GUI** | HTML5 / CSS3 | Modern dark-mode layout using CSS variables, Flexbox/Grid, and glassmorphism |
| **Frontend Script**| Vanilla JavaScript (ES6+) | Socket.IO client logic, DOM rendering, audio/desktop notifications |
| **Testing** | `unittest` / `pytest` | Automated unit and integration testing suite |

---

## 🏗️ Architecture & Component Design

The application follows a modular, layered architecture adhering to the **Separation of Concerns** principle:

```
                  ┌────────────────────────────────────────┐
                  │          Browser / Web Client          │
                  │   HTML5 / CSS3 / ES6 / Socket.IO UI    │
                  └──────────────────┬─────────────────────┘
                                     │ HTTP / WebSockets
                                     ▼
                  ┌────────────────────────────────────────┐
                  │             Flask App Engine           │
                  │   (app.py & config.py configuration)   │
                  └──────────┬──────────────────┬──────────┘
                             │                  │
               HTTP Routes   │                  │ Socket Events
                             ▼                  ▼
              ┌────────────────────┐      ┌────────────────────┐
              │   auth/ Blueprint   │      │ chat/ Event Engine │
              │  (routes & service)│      │  (events & rooms)  │
              └──────────┬─────────┘      └─────────┬──────────┘
                         │                          │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                       ┌────────────────────────────┐
                       │      models/ & utils/      │
                       │ (Validators, Security,     │
                       │  Emoji Parser, Data Models)│
                       └──────────────┬─────────────┘
                                      │
                                      ▼
                       ┌────────────────────────────┐
                       │    database/ (db.py)       │
                       │    SQLite Persistent DB    │
                       └────────────────────────────┘
```

### Directory Hierarchy

```
Chat Application/
├── app.py                      # Flask & Socket.IO server entrypoint
├── config.py                   # Centralized environment configuration
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete documentation
├── .env.example                # Safe environment variable placeholders
├── .gitignore                  # Git tracking rules
│
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite connection pooling & schema initialization
│   ├── schema.sql              # Relational SQL schema definitions
│   └── chat.db                 # SQLite database file (gitignored)
│
├── auth/
│   ├── __init__.py
│   ├── routes.py               # Flask authentication endpoints (/login, /register, /logout)
│   └── service.py              # User authentication business logic
│
├── chat/
│   ├── __init__.py
│   ├── events.py               # Socket.IO event handler endpoints
│   ├── service.py              # Messaging service & history pagination
│   └── rooms.py                # Room manager & active user presence tracker
│
├── models/
│   ├── __init__.py
│   ├── user.py                 # User domain entity model
│   ├── room.py                 # Room domain entity model
│   └── message.py              # Message domain entity model
│
├── utils/
│   ├── __init__.py
│   ├── validators.py           # Input validation helpers
│   ├── security.py             # HTML escaping & session security utilities
│   └── emoji.py                # Emoji shortcode replacement parser
│
├── templates/
│   ├── login.html              # Dark-mode login view
│   ├── register.html           # User registration view
│   └── chat.html               # Main real-time chat interface
│
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphic dark styling
│   └── js/
│       └── chat.js             # Client-side Socket.IO & notification engine
│
└── tests/
    ├── __init__.py
    ├── test_auth.py            # Registration & hashing tests
    ├── test_database.py        # Schema & constraint tests
    ├── test_rooms.py           # Room creation & presence tests
    ├── test_messages.py        # XSS, history & emoji tests
    └── test_socket_events.py   # Socket.IO integration tests
```

---

## 🗄️ Database Schema & Design

### Relational Schema (`database/schema.sql`)

```sql
PRAGMA foreign_keys = ON;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Room Members Table
CREATE TABLE IF NOT EXISTS room_members (
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_messages_room_timestamp ON messages(room_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_rooms_name ON rooms(name);
```

---

## ⚡ Socket.IO Event Architecture

| Event Name | Direction | Payload Specs | Server Action & Broadcast Behavior |
| :--- | :--- | :--- | :--- |
| `connect` | Client -> Server | Session cookie | Validates Flask session context. Rejects connection if unauthenticated. |
| `disconnect` | Client -> Server | None | Cleans up socket presence; emits `system_message` and `presence_update` to room. |
| `get_rooms` | Client -> Server | None | Fetches all room records from SQLite; emits `room_list` to caller. |
| `create_room` | Client -> Server | `{ room_name }` | Validates name uniqueness; inserts room; broadcasts updated `room_list` to all clients. |
| `join_room` | Client -> Server | `{ room_name }` | Joins Socket channel; loads 50 recent messages; emits `message_history` to caller; broadcasts `presence_update` to room. |
| `leave_room` | Client -> Server | `{ room_name }` | Leaves Socket channel; updates presence; broadcasts `user_left` system notification. |
| `send_message` | Client -> Server | `{ room_name, content }` | Validates length; escapes HTML; replaces emoji shortcodes; saves to SQLite; broadcasts `receive_message` to room members. |
| `receive_message` | Server -> Client | `{ id, sender, content, timestamp, room_name }` | Renders message bubble in message feed; triggers desktop notification if tab is blurred. |

---

## 🔒 Security Architecture & Disclosures

### Implemented Security Controls
1. **Parameterized Queries (Anti-SQLi)**: Every SQLite operation uses standard parameter tuple bindings (`cursor.execute("SELECT ... WHERE username = ?", (username,))`).
2. **Server-Side Sanitization (Anti-XSS)**: User input is escaped via `markupsafe.escape` / `html.escape` before database insertion or event broadcasting.
3. **Client-Side Safe Rendering**: Frontend message elements render text using safe DOM node bindings.
4. **Werkzeug Password Hashing**: Passwords are never stored in raw text; hashed using `scrypt`/`pbkdf2`.
5. **Session Security**: Session cookies signed via configurable `SECRET_KEY`.

### ⚠️ Explicit Privacy & Limitations Disclosure
- **Data Storage**: All chat messages, room names, and user accounts are persisted locally in SQLite (`database/chat.db`).
- **Password Hashing**: Passwords are securely hashed. Raw passwords are never logged, displayed, or stored.
- **Message Content Encryption**: **Chat message contents are NOT end-to-end encrypted (E2EE)**. Messages are stored as sanitized plain text within SQLite for educational and portfolio presentation purposes.
- **Transport Layer**: Localhost HTTP/WS communication runs unencrypted. Production deployment would require SSL/TLS (`https://` and `wss://`).

---

## ⚡ Installation & Execution Guide

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)

### 1. Clone & Navigate
```bash
cd "e:\Projects\Chat Application"
```

### 2. Environment Configuration
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run Development Server
```bash
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

The application includes a test suite covering authentication, database schema, room management, message security, and Socket.IO events.

Execute all tests:
```bash
python -m unittest discover tests
```

Expected Output:
```text
Ran 18 tests in 2.232s
OK
```

---

## 🎓 Learning Outcomes & Portfolio Summary

- Developed a real-time event-driven Python application using **Flask-SocketIO**.
- Architected a clean relational schema in **SQLite** with parameterized queries and index tuning.
- Built production-ready **Werkzeug password hashing** and session-based authentication.
- Designed a modern, responsive **glassmorphic UI** using Vanilla CSS3 and ES6 JavaScript.
- Implemented **XSS and SQL injection defenses**, input validation, and desktop notifications.
- Written automated unit and integration tests using Python's native `unittest` framework.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

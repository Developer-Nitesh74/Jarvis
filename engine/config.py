import sqlite3
import os

# DB file lives next to this module
DB_PATH = os.path.join(os.path.dirname(__file__), "jarvis.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create all tables if they don't exist and seed default owner info."""
    conn = get_connection()
    c = conn.cursor()

    # Owner personal info
    c.execute("""
        CREATE TABLE IF NOT EXISTS owner (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL DEFAULT 'User',
            designation TEXT DEFAULT 'Iron Man',
            mobile TEXT DEFAULT '',
            email TEXT DEFAULT '',
            city TEXT DEFAULT 'Earth'
        )
    """)

    # Custom system commands (keyword -> executable path)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sys_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            path TEXT NOT NULL
        )
    """)

    # Custom web commands (keyword -> url)
    c.execute("""
        CREATE TABLE IF NOT EXISTS web_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            url TEXT NOT NULL
        )
    """)

    # Phone book / contacts
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT DEFAULT '',
            city TEXT DEFAULT ''
        )
    """)

    # Chat history
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed owner row if empty
    c.execute("SELECT COUNT(*) FROM owner")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO owner (id, name, designation, mobile, email, city) VALUES (1, 'Sir', 'Iron Man', '', '', 'Earth')")

    # Seed some default web commands
    c.execute("SELECT COUNT(*) FROM web_commands")
    if c.fetchone()[0] == 0:
        defaults = [
            ("google",    "https://www.google.com"),
            ("youtube",   "https://www.youtube.com"),
            ("github",    "https://www.github.com"),
            ("instagram", "https://www.instagram.com"),
            ("twitter",   "https://www.twitter.com"),
        ]
        c.executemany("INSERT INTO web_commands (keyword, url) VALUES (?, ?)", defaults)

    conn.commit()
    conn.close()


# ── Owner ──────────────────────────────────────────────────────────────────────

def get_owner_info():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, designation, mobile, email, city FROM owner WHERE id=1")
    row = c.fetchone()
    conn.close()
    return list(row) if row else ["User", "", "", "", ""]

def update_owner_info(name, designation, mobile, email, city):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE owner SET name=?, designation=?, mobile=?, email=?, city=?
        WHERE id=1
    """, (name, designation, mobile, email, city))
    conn.commit()
    conn.close()


# ── System Commands ────────────────────────────────────────────────────────────

def get_sys_commands():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, keyword, path FROM sys_commands ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_sys_command(keyword, path):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO sys_commands (keyword, path) VALUES (?, ?)", (keyword.lower(), path))
    conn.commit()
    conn.close()

def delete_sys_command(cmd_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sys_commands WHERE id=?", (int(cmd_id),))
    conn.commit()
    conn.close()


# ── Web Commands ───────────────────────────────────────────────────────────────

def get_web_commands():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, keyword, url FROM web_commands ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_web_command(keyword, url):
    if not url.startswith("http"):
        url = "https://" + url
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO web_commands (keyword, url) VALUES (?, ?)", (keyword.lower(), url))
    conn.commit()
    conn.close()

def delete_web_command(cmd_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM web_commands WHERE id=?", (int(cmd_id),))
    conn.commit()
    conn.close()


# ── Contacts ───────────────────────────────────────────────────────────────────

def get_contacts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, mobile, email, city FROM contacts ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return rows

def add_contact(name, mobile, email="", city=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, mobile, email, city) VALUES (?, ?, ?, ?)",
              (name, mobile, email, city))
    conn.commit()
    conn.close()

def delete_contact(contact_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE id=?", (int(contact_id),))
    conn.commit()
    conn.close()


# ── Chat History ───────────────────────────────────────────────────────────────

def save_chat(sender: str, message: str):
    """Save a chat message to the history."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def get_chat_history():
    """Retrieve all chat history ordered by timestamp."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT sender, message, timestamp FROM chat_history ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

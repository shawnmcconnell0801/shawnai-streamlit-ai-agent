
import sqlite3

# DATABASE CONFIGURATION
DB_NAME = "shawnaI.db"


# CREATE DATABASE CONNECTION
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# INITIALIZE DATABASE TABLES
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Store conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            title TEXT NOT NULL
        )
    """)

    # Store individual messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (chat_id)
                REFERENCES chats(chat_id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# SAVE OR UPDATE A CHAT
def save_chat(chat_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chats (chat_id, title)
        VALUES (?, ?)
        ON CONFLICT(chat_id)
        DO UPDATE SET title = excluded.title
    """, (chat_id, title))

    conn.commit()
    conn.close()


# SAVE A MESSAGE
def save_message(chat_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (chat_id, role, content)
        VALUES (?, ?, ?)
    """, (chat_id, role, content))

    conn.commit()
    conn.close()


# LOAD ALL CONVERSATIONS
def load_chats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chat_id, title
        FROM chats
        ORDER BY rowid DESC
    """)

    chats = cursor.fetchall()
    conn.close()

    return chats


# LOAD MESSAGES FOR A SPECIFIC CHAT
def load_messages(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE chat_id = ?
        ORDER BY id ASC
    """, (chat_id,))

    messages = cursor.fetchall()
    conn.close()

    return [
        {"role": role, "content": content}
        for role, content in messages
    ]


# DELETE A CONVERSATION
def delete_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM chats
        WHERE chat_id = ?
    """, (chat_id,))

    conn.commit()
    conn.close()


# CLEAR MESSAGES WITHOUT DELETING THE CHAT
def clear_chat_messages(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE chat_id = ?
    """, (chat_id,))

    conn.commit()
    conn.close()

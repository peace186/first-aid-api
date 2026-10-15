import os
import sqlite3

# Remove existing file to start fresh
if os.path.exists("app_data.db"):
    os.remove("app_data.db")

conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

# Enable foreign keys and create tables
cursor.executescript("""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon_name TEXT
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    warning_note TEXT,
    is_emergency INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    headline TEXT NOT NULL,
    details TEXT,
    image_path TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
);
""")

conn.commit()
conn.close()

print("SUCCESS: Database and all tables created cleanly!")
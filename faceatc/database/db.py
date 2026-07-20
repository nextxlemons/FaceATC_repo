"""
SQLite connection handling and schema initialization.
"""
import sqlite3
from contextlib import contextmanager
from config import DB_PATH, ensure_dirs


@contextmanager
def get_connection():
    """Context-managed SQLite connection — always closes, even on error."""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                image_path TEXT NOT NULL,
                total_attendance INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course TEXT NOT NULL,
                lecture_name TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        ''')

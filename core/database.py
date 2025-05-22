import sqlite3
from threading import Lock
from .config import DB_PATH

sqlite_lock = Lock()

def init_db():
    with sqlite_lock, sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS optimizations (
                filename TEXT,
                original_size REAL,
                optimized_size REAL,
                percent_reduction REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                failed INTEGER DEFAULT 0
            )
        """)

def get_optimizations():
    with sqlite_lock, sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("SELECT filename, original_size, optimized_size, percent_reduction, failed FROM optimizations ORDER BY timestamp DESC")
        rows = c.fetchall()
        return rows

def log_optimization(filename, orig_size, opt_size, failed=0):
    percent = round(100 * (orig_size - opt_size) / orig_size, 2) if orig_size > 0 else 0
    with sqlite_lock, sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute(
            "INSERT INTO optimizations (filename, original_size, optimized_size, percent_reduction, failed) VALUES (?, ?, ?, ?, ?)",
            (filename, orig_size / (1024*1024), opt_size / (1024*1024), percent, failed)
        )

def clear_optimizations():
    with sqlite_lock, sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM optimizations")
        conn.commit()
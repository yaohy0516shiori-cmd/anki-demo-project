import sqlite3
from pathlib import Path

def create_connection(db_path:str)->sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def close_connection(conn:sqlite3.Connection):
    conn.close()
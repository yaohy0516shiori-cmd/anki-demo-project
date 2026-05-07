import sqlite3
from pathlib import Path
from contextlib import contextmanager

def create_connection(db_path:str)->sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def close_connection(conn:sqlite3.Connection):
    conn.close()

class SqliteTransactionManager:
    def __init__(self, conn: sqlite3.Connection):
        self.__conn = conn

    @contextmanager
    def transaction(self):
        try:
            self.__conn.execute("BEGIN")
            yield
        except Exception:
            self.__conn.rollback()
            raise
        else:
            self.__conn.commit()
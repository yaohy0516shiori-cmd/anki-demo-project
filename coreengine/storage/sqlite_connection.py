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
        self.__commit_count = 0

    @contextmanager
    def transaction(self):
        # if the commit count is greater than 0, then we are already in a transaction
        # so we just need to increment the commit count and yield to the caller
        if self.__commit_count > 0:
            self.__commit_count += 1
            try:
                yield
            except Exception:
                self.__conn.rollback()
                raise
            finally:
                self.__commit_count -= 1
            return
        try:
            # start a transaction
            self.__conn.execute("BEGIN")
            self.__commit_count = 1
            # stop, yield to the caller
            yield
        except Exception:
            # if an error occurs, rollback the transaction
            self.__conn.rollback()
            raise
        else:
            # if the transaction is successful, commit the transaction
            self.__conn.commit()
        finally:
            self.__commit_count = 0
from pathlib import Path
import sqlite3

def init_db(conn:sqlite3.Connection):
    # find schema.sql
    schema_path=Path(__file__).with_name("schema.sql")
    # read path as a string
    sql=schema_path.read_text(encoding='utf-8')
    # execute the whole sql
    conn.executescript(sql)
    # submit
    conn.commit()
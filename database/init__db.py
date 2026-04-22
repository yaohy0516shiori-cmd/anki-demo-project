from coreengine.storage.sqlite_connection import create_connection, close_connection
from coreengine.storage.schema import init_db

def main():
    conn = create_connection("database/anki_demo.db")
    try:
        init_db(conn)
        print("Database initialized successfully.")
    finally:
        close_connection(conn)

if __name__ == "__main__":
    main()
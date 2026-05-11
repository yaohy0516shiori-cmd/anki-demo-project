import sqlite3

from ..user.usermodel import User
from ..user.user_repository import UserRepository


class SqliteUserRepository(UserRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.__conn = conn

    def __deserialize_user(self, row: sqlite3.Row) -> User:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            username=row["username"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add_user(self, user: User) -> int:
        if user.user_id is not None:
            raise ValueError("User ID must be None")

        cursor = self.__conn.execute("""
        INSERT INTO user (
            email,
            username,
            password_hash,
            phone,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user.email,
            user.username,
            user.password_hash,
            user.phone,
            user.created_at,
            user.updated_at,
        ))

        return cursor.lastrowid

    def get_user(self, user_id: int) -> User:
        row = self.__conn.execute("""
        SELECT * FROM user
        WHERE user_id = ?
        """, (user_id,)).fetchone()

        if row is None:
            raise ValueError("User not found")

        return self.__deserialize_user(row)

    def get_user_by_email(self, email: str) -> User | None:
        row = self.__conn.execute("""
        SELECT * FROM user
        WHERE email = ?
        """, (email,)).fetchone()

        if row is None:
            return None

        return self.__deserialize_user(row)

    def get_user_by_username(self, username: str) -> User | None:
        row = self.__conn.execute("""
        SELECT * FROM user
        WHERE username = ?
        """, (username,)).fetchone()

        if row is None:
            return None

        return self.__deserialize_user(row)

    def update_user_name(self, user_id: int, username: str) -> User:
        cursor = self.__conn.execute("""
        UPDATE user
        SET username = ?
        WHERE user_id = ?
        """, (username, user_id))

        if cursor.rowcount == 0:
            raise ValueError("User not found")

        return self.get_user(user_id)

    def update_user_email(self, user_id: int, email: str) -> User:
        cursor = self.__conn.execute("""
        UPDATE user
        SET email = ?
        WHERE user_id = ?
        """, (email, user_id))

        if cursor.rowcount == 0:
            raise ValueError("User not found")

        return self.get_user(user_id)

    def update_user_password(self, user_id: int, password: str) -> User:
        cursor = self.__conn.execute("""
        UPDATE user
        SET password_hash = ?
        WHERE user_id = ?
        """, (password, user_id))

        if cursor.rowcount == 0:
            raise ValueError("User not found")

        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> int:
        cursor = self.__conn.execute("""
        DELETE FROM user
        WHERE user_id = ?
        """, (user_id,))

        if cursor.rowcount == 0:
            raise ValueError("User not found")

        return cursor.rowcount
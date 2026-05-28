from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from coreengine.user.usermodel import User
from coreengine.user.user_repository import UserRepository
from coreengine.storage.sqlalchemy_models import UserORM


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: DbSession):
        self.__db = db

    def __to_domain(self, orm: UserORM) -> User:
        return User(
            user_id=orm.user_id,
            email=orm.email,
            username=orm.username,
            password_hash=orm.password_hash,
            phone=orm.phone,
            created_at=orm.created_at.isoformat() if orm.created_at else None,
            updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        )

    def add_user(self, user: User) -> int:
        if user.user_id is not None:
            raise ValueError("User ID must be None")

        orm = UserORM(
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            phone=user.phone,
        )

        try:
            self.__db.add(orm)
            self.__db.flush()
        except IntegrityError as exc:
            raise ValueError("Email or username already exists") from exc

        return orm.user_id

    def get_user(self, user_id: int) -> User:
        orm = self.__db.get(UserORM, user_id)
        if orm is None:
            raise ValueError("User not found")
        return self.__to_domain(orm)

    def get_user_by_email(self, email: str) -> User:
        stmt = select(UserORM).where(UserORM.email == email)
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("User not found")
        return self.__to_domain(orm)

    def get_user_by_username(self, username: str) -> User:
        stmt = select(UserORM).where(UserORM.username == username)
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("User not found")
        return self.__to_domain(orm)

    def update_user_name(self, user_id: int, username: str) -> User:
        orm = self.__db.get(UserORM, user_id)
        if orm is None:
            raise ValueError("User not found")

        orm.username = username
        self.__db.flush()
        return self.__to_domain(orm)

    def update_user_email(self, user_id: int, email: str) -> User:
        orm = self.__db.get(UserORM, user_id)
        if orm is None:
            raise ValueError("User not found")

        orm.email = email
        self.__db.flush()
        return self.__to_domain(orm)

    def update_user_password(self, user_id: int, password: str) -> User:
        orm = self.__db.get(UserORM, user_id)
        if orm is None:
            raise ValueError("User not found")

        orm.password_hash = password
        self.__db.flush()
        return self.__to_domain(orm)

    def delete_user(self, user_id: int) -> None:
        orm = self.__db.get(UserORM, user_id)
        if orm is None:
            raise ValueError("User not found")

        self.__db.delete(orm)
        self.__db.flush()
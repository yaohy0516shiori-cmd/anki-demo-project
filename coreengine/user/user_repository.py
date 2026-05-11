from abc import ABC, abstractmethod
from .usermodel import User

class UserRepository(ABC):
    @abstractmethod
    def add_user(self, user: User) -> User:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> User:
        pass

    @abstractmethod
    def update_user_name(self, user_id: int, username: str) -> User:
        pass

    @abstractmethod
    def update_user_email(self, user_id: int, email: str) -> User:
        pass

    @abstractmethod
    def update_user_password(self, user_id: int, password: str) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass
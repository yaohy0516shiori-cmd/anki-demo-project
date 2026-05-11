from contextlib import nullcontext
from .usermodel import User
from ..deck.deckmodel import Deck
from ..deck.deck_repository import DeckRepository
from .user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository, deck_repo: DeckRepository, transaction_manager=None):
        self.__user_repo=user_repository
        self.__transaction_manager=transaction_manager
        self.__deck_repo=deck_repo

    def __transaction(self):
        if self.__transaction_manager is None:
            return nullcontext()
        return self.__transaction_manager.transaction()
    
    def register_user(self, email: str, username: str, password: str):
        if self.__user_repo.get_user_by_email(email) is not None:
            raise ValueError("Email already exists")
        
        with self.__transaction():
            user = User(email=email, username=username, password_hash=password)
            user_id = self.__user_repo.add_user(user)

            default_deck=Deck(
                deck_name="Default",
                deck_description=f"Default deck for the user {username}",
                user_id=user_id,
                is_default=True
            )

            self.__deck_repo.create_deck(default_deck)

        return user_id

    def login(self, email: str, password: str):
        user = self.__user_repo.get_user_by_email(email)
        if user is None:
            raise ValueError("User not found")
        if user.password_hash != password:
            raise ValueError("Invalid password")
        return user
    
    def get_user(self, user_id: int):
        return self.__user_repo.get_user(user_id)
    
    def get_user_by_email(self, email: str):
        return self.__user_repo.get_user_by_email(email)
    
    def get_user_by_username(self, username: str):
        return self.__user_repo.get_user_by_username(username)
    
    def update_user_name(self, user_id: int, username: str):
        return self.__user_repo.update_user_name(user_id, username)
    
    def update_user_email(self, user_id: int, email: str):
        return self.__user_repo.update_user_email(user_id, email)
    
    def update_user_password(self, user_id: int, password: str):
        return self.__user_repo.update_user_password(user_id, password)
    
    def delete_user(self, user_id: int):
        return self.__user_repo.delete_user(user_id)
    
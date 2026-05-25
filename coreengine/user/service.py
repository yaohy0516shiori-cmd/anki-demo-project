from contextlib import nullcontext
from .usermodel import User
from ..deck.deckmodel import Deck
from ..deck.deck_repository import DeckRepository
from .user_repository import UserRepository
import hashlib
import hmac
import secrets

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
        email = email.strip().lower()

        if self.__user_repo.get_user_by_email(email) is not None:
            raise ValueError("Email already exists")
        
        with self.__transaction():
            user = User(email=email, username=username, password_hash=hash_password(password))
            user_id = self.__user_repo.add_user(user)

            self.__deck_repo.ensure_created(user_id)

        return user_id

    def login(self, email: str, password: str):
        user = self.__user_repo.get_user_by_email(email)
        if user is None:
            raise ValueError("User not found")
        if not verify_password(password, user.password_hash) or user is None:
            raise ValueError("Invalid password or email")
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
        password_hash = hash_password(password)
        return self.__user_repo.update_user_password(user_id, password_hash)
    
    def delete_user(self, user_id: int):
        return self.__user_repo.delete_user(user_id)

    def get_password_hash(self, password: str):
        return hash_password(password)

    def reset_password_by_email(self, email: str, new_password: str):
        email = email.strip().lower()

        user = self.__user_repo.get_user_by_email(email)
        if user is None:
            raise ValueError("User not found")

        return self.update_user_password(user.user_id, new_password)
    
    def change_password(self, user_id: int, old_password: str, new_password: str):
        user = self.__user_repo.get_user(user_id)

        if not verify_password(old_password, user.password_hash):
            raise ValueError("Old password is incorrect")

        return self.update_user_password(user_id, new_password)
    
def hash_password(password: str):
    salt = secrets.token_hex(16)
    interations=100_000
    digest=hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), interations, dklen=32).hex()
    return f"pbkdf2_sha256${interations}${salt}${digest}"
    
def verify_password(password: str, password_hash: str):
    try:
        algorithm, interations, salt, expected = password_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
            
        digest=hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(interations), dklen=32).hex()
        return hmac.compare_digest(digest, expected)
    except Exception:
        return False
    

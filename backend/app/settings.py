# read environment variables from .env file
from functools import lru_cache
# use pydantic_settings to read environment variables from .env file
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # database url
    database_url: str = (
        "postgresql+psycopg://memory_flashcards_user:"
        "memory_flashcards_password@localhost:5432/memory_flashcards"
    )
    # redis url
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "dev-only-change-me"
    # algorithm for jwt
    algorithm: str = "HS256"
    # access token expire minutes
    access_token_expire_minutes: int = 60 
    # model config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",extra="ignore")

# use lru_cache to cache the settings
@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

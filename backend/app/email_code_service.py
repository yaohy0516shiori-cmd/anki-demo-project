# backend/app/email_code_service.py

from datetime import datetime, timedelta, timezone
import random


class InMemoryEmailCodeService:
    def __init__(self, ttl_minutes: int = 5):
        self.__ttl_minutes = ttl_minutes
        self.__codes: dict[tuple[str, str], dict] = {}

    def generate_code(self, email: str, purpose: str) -> str:
        self.__cleanup_expired()

        normalized_email = self.__normalize_email(email)
        normalized_purpose = self.__normalize_purpose(purpose)
        code = f"{random.randint(0, 999999):06d}"

        self.__codes[(normalized_email, normalized_purpose)] = {
            "code": code,
            "expires_at": datetime.now(timezone.utc)
            + timedelta(minutes=self.__ttl_minutes),
        }

        return code

    def verify_code(self, email: str, purpose: str, code: str) -> bool:
        self.__cleanup_expired()

        normalized_email = self.__normalize_email(email)
        normalized_purpose = self.__normalize_purpose(purpose)
        key = (normalized_email, normalized_purpose)

        record = self.__codes.get(key)
        if record is None:
            return False

        if datetime.now(timezone.utc) > record["expires_at"]:
            del self.__codes[key]
            return False

        if record["code"] != str(code).strip():
            return False

        # 验证码一次性使用，成功后立刻删除
        del self.__codes[key]
        return True

    def __cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)

        expired_keys = [
            key
            for key, value in self.__codes.items()
            if now > value["expires_at"]
        ]

        for key in expired_keys:
            del self.__codes[key]

    def __normalize_email(self, email: str) -> str:
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required")

        return email.strip().lower()

    def __normalize_purpose(self, purpose: str) -> str:
        if purpose not in {"register", "password_reset"}:
            raise ValueError("Unsupported email code purpose")

        return purpose

from redis import Redis

class RedisEmailCodeService:
    def __init__(self, redis: Redis, ttl_seconds: int = 300, cooloff_seconds: int = 60):
        self.__redis = redis
        self.__ttl_seconds = ttl_seconds
        self.__cooloff_seconds = cooloff_seconds

    def generate_code(self, email: str, purpose: str) -> str:
        normalized_email = self.__normalize_email(email)
        normalized_purpose = self.__normalize_purpose(purpose)
        cooldown_key=self.__cooldown_key(normalized_email, normalized_purpose)
        cooldown_create=self.__redis.set(cooldown_key, "1", ex=self.__cooloff_seconds)

        if not cooldown_create:
            ttl=self.__redis.ttl(cooldown_key)
            wait_seconds=ttl if ttl > 0 else self.__cooloff_seconds
            raise ValueError(f"Please wait {wait_seconds} seconds before sending another code")
        
        code=f"{random.randint(0, 999999):06d}"

        code_key=self.__code_key(normalized_email, normalized_purpose)

        success=self.__redis.set(code_key, code, ex=self.__ttl_seconds, nx=True)

        return code if success else None
    
    def verify_code(self, email: str, purpose: str, code: str) -> bool:
        normalized_email = self.__normalize_email(email)
        normalized_purpose = self.__normalize_purpose(purpose)
        normalized_code=str(code).strip()

        code_key=self.__code_key(normalized_email, normalized_purpose)
        
        stored_code=self.__redis.get(code_key)
        if stored_code is None:
            return False
        
        if stored_code != normalized_code:
            return False
        
        self.__redis.delete(code_key)
        return True
    
    def __cooldown_key(self, email: str, purpose: str) -> str:
        return f"email_code:cooldown:{email}:{purpose}"
    
    def __code_key(self, email: str, purpose: str) -> str:
        return f"email_code:code:{email}:{purpose}"
    
    def __normalize_email(self, email: str) -> str:
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required")
        return email.strip().lower()
    
    def __normalize_purpose(self, purpose: str) -> str:
        if purpose not in {"register", "password_reset"}:
            raise ValueError("Unsupported email code purpose")
        return purpose
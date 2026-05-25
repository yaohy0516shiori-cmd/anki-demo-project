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
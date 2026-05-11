from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class User:
    email: str
    username: str
    password_hash: str
    phone: str | None = None
    user_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self):
        if not isinstance(self.email, str) or not self.email.strip():
            raise ValueError("Email is required")
        if not isinstance(self.username, str) or not self.username.strip():
            raise ValueError("Username is required")
        if not isinstance(self.password_hash, str) or not self.password_hash:
            raise ValueError("Password hash is required")
        if self.user_id is not None:
            if not isinstance(self.user_id, int) or self.user_id <= 0:
                raise ValueError("User id must be an integer and positive")

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.email = self.email.strip()
        self.username = self.username.strip()
        self.password_hash = self.password_hash.strip()
        self.created_at = self.created_at or now
        self.updated_at = self.updated_at or now
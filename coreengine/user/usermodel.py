from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class User:
    email: str
    phone: str | None = None
    username: str
    password_hash: str
    user_id: int 
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self):
        if not isinstance(self.email, str) or not self.email.strip():
            raise ValueError("Email is required")
        if not isinstance(self.username, str) or not self.username.strip():
            raise ValueError("Username is required")
        if not isinstance(self.password_hash, str) or not self.password_hash:
            raise ValueError("Password hash is required")
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("User id is required")

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.created_at = self.created_at or now
        self.updated_at = self.updated_at or now
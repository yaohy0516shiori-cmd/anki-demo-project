from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

@dataclass
class Session:
    today: date
    deck_id: int
    session_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "active"
    learning_queue: list[int] = field(default_factory=list)
    review_queue: list[int] = field(default_factory=list)
    new_queue: list[int] = field(default_factory=list)
    current_card_id: Optional[int] = None
    current_hint_used: bool = False
    current_back_revealed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def create(deck_id: int, today: date):
        now=datetime.now()
        return Session(
            deck_id=deck_id,
            today=today,
            created_at=now,
            updated_at=now
        )
    def touch(self):
        self.updated_at=datetime.now()
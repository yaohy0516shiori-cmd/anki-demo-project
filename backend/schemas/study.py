from datetime import date
from pydantic import BaseModel


class StudySessionStart(BaseModel):
    deck_id: int
    today: date | None = None


class StudyRating(BaseModel):
    rating: str


class StudySessionStartOut(BaseModel):
    user_id: int
    session_id: str
    deck_id: int
    deck_name: str
    learning_queue: int
    review_queue: int
    new_queue: int


class StudyCardOut(BaseModel):
    card_id: int
    note_id: int
    deck_id: int
    template_ord: int
    status: str
    due: str
    interval: int
    ease: float
    reps: int
    lapses: int
    step_index: int | None = None


class StudyNoteOut(BaseModel):
    note_id: int
    note_type_id: int
    fields: list[str]
    tags: list[str]
    hint: str
    sort_field: str
    checksum: str
    created_at: str
    updated_at: str


class StudyNextOut(BaseModel):
    finished: bool
    user_id: int
    session_id: str
    card: StudyCardOut | None = None
    note: StudyNoteOut | None = None
    front: str | None = None
    status: str | None = None
    step_index: int | None = None
    deck_id: int | None = None
    hint_available: bool = False

    
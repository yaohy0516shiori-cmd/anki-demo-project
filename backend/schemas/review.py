from pydantic import BaseModel


class ReviewLogOut(BaseModel):
    review_log_id: int
    card_id: int
    deck_id: int
    rating: str
    old_status: str
    new_status: str
    old_due: str | None = None
    new_due: str | None = None
    old_interval: int
    new_interval: int
    old_ease: float
    new_ease: float
    old_lapses: int
    new_lapses: int
    old_reps: int
    new_reps: int
    old_step_index: int | None = None
    new_step_index: int | None = None
    hint_used: bool
    review_time: str
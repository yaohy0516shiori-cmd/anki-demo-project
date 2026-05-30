from pydantic import BaseModel

class DashboardCardOut(BaseModel):
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
    note_type_id: int
    content: str
    tags: list[str]
    hint: str
    created_at: str
    updated_at: str

class DashboardCardPageOut(BaseModel):
    items: list[DashboardCardOut]
    page: int
    page_size: int
    total: int
    total_pages: int

class DashboardSummaryOut(BaseModel):
    total_decks: int
    total_notes: int
    total_cards: int
    due_today_cards: int
    new_cards: int
    learning_cards: int
    review_cards: int
    relearning_cards: int
    total_reviews: int
    today_reviews: int
    good_reviews: int
    again_reviews: int
    lastest_review_time: str | None = None

class DeckLearningStatsOut(BaseModel):
    deck_id: int
    deck_name: str
    deck_description: str
    is_default: bool
    card_count: int
    due_today_count: int
    new_count: int
    learning_count: int
    review_count: int
    relearning_count: int
    review_log_count: int
    good_count: int
    again_count: int
    latest_review_time: str | None = None

class DailyReviewStatsOut(BaseModel):
    date: str
    review_count: int
    good_count: int
    again_count: int
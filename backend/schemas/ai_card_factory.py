from pydantic import BaseModel, Field


class AICardDraftGenerateRequest(BaseModel):
    source_text: str = Field(min_length=1)
    user_prompt: str = ""
    deck_id: int | None = None
    note_type_id: int | None = None
    max_cards: int = Field(default=10, ge=1, le=30)
    language: str = "zh"


class AICardDraftReviseRequest(BaseModel):
    user_instruction: str = Field(min_length=1)
    language: str = "zh"


class AICardDraftConfirmRequest(BaseModel):
    accepted_item_ids: list[int]
    rejected_item_ids: list[int] = []


class AICardDraftVersionOut(BaseModel):
    version_id: int
    version_no: int
    fields: list[str]
    tags: list[str]
    hint: str
    reason: str
    user_instruction: str
    created_by: str
    created_at: str | None


class AICardDraftItemOut(BaseModel):
    item_id: int
    note_type_id: int
    status: str
    created_note_id: int | None
    error_message: str
    latest_version: AICardDraftVersionOut


class AICardDraftBatchOut(BaseModel):
    batch_id: int
    user_id: int
    deck_id: int | None
    source_type: str
    source_text: str
    user_prompt: str
    status: str
    created_at: str | None
    updated_at: str | None
    items: list[AICardDraftItemOut]


class AICardDraftConfirmOut(BaseModel):
    batch_id: int
    created_note_ids: list[int]
    created_note_count: int
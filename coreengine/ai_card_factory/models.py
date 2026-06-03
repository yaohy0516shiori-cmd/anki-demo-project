from dataclasses import dataclass


@dataclass
class CardDraftBatch:
    user_id: int
    deck_id: int | None
    source_type: str
    source_text: str
    user_prompt: str
    status: str
    batch_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class CardDraftItem:
    batch_id: int
    user_id: int
    note_type_id: int
    status: str
    item_id: int | None = None
    created_note_id: int | None = None
    error_message: str = ""
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class CardDraftVersion:
    item_id: int
    user_id: int
    version_no: int
    fields: list[str]
    tags: list[str]
    hint: str
    reason: str
    user_instruction: str
    created_by: str
    version_id: int | None = None
    created_at: str | None = None


@dataclass
class CardDraftWithLatestVersion:
    item: CardDraftItem
    latest_version: CardDraftVersion
from pydantic import BaseModel


class DeckCreate(BaseModel):
    deck_name: str
    deck_description: str = ""


class DeckUpdate(BaseModel):
    deck_name: str | None = None
    deck_description: str | None = None


class DeckOut(BaseModel):
    deck_id: int
    deck_name: str
    deck_description: str
    created_at: str
    updated_at: str
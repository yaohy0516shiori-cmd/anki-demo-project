from pydantic import BaseModel
from typing import List


class NoteCreate(BaseModel):
    note_type_id: int
    fields: List[str]
    tags: List[str] = []
    hint: str = ""
    deck_id: int 


class NoteUpdate(BaseModel):
    fields: List[str] | None = None
    tags: List[str] | None = None
    hint: str | None = None


class NoteOut(BaseModel):
    note_id: int
    note_type_id: int
    fields: List[str]
    tags: List[str]
    hint: str
    sort_field: str
    checksum: str
    created_at: str
    updated_at: str
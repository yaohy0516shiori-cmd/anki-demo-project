from dataclasses import dataclass
from typing import Protocol


@dataclass
class GeneratedCardDraft:
    note_type_id: int
    fields: list[str]
    tags: list[str]
    hint: str = ""
    reason: str = ""


class CardDraftProvider(Protocol):
    def generate_drafts(
        self,
        source_text: str,
        user_prompt: str,
        note_type_id: int | None,
        max_cards: int,
        language: str,
    ) -> list[GeneratedCardDraft]:
        ...

    def revise_drafts(
        self,
        current_drafts: list[GeneratedCardDraft],
        user_instruction: str,
        language: str,
    ) -> list[GeneratedCardDraft]:
        ...
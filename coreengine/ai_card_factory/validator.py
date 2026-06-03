import re
from coreengine.ai_card_factory.provider import GeneratedCardDraft
from coreengine.note_type.type_registry import get_note_type

_CLOZE_PATTERN = re.compile(r"\{\{c(\d+)::.+?\}\}")

class CardDraftValidator:
    def validate_generated_draft(self, draft: GeneratedCardDraft) -> bool:
        if not isinstance(draft.note_type_id, int):
            raise ValueError("note_type_id must be an integer")

        note_type = get_note_type(draft.note_type_id)

        if not isinstance(draft.fields, list):
            raise ValueError("fields must be a list")

        if not all(isinstance(field, str) for field in draft.fields):
            raise ValueError("fields must be a list of strings")

        if len(draft.fields) != len(note_type.field_names):
            raise ValueError("fields count does not match note type")

        if not isinstance(draft.tags, list):
            raise ValueError("tags must be a list")

        if not all(isinstance(tag, str) for tag in draft.tags):
            raise ValueError("tags must be a list of strings")

        if not isinstance(draft.hint, str):
            raise ValueError("hint must be a string")

        if note_type.kind == "cloze":
            self._validate_cloze(draft.fields[0])

    def _validate_cloze(self, text: str) -> None:
        matches = _CLOZE_PATTERN.findall(text)

        if not matches:
            raise ValueError("cloze note must contain at least one {{c1::...}} block")

        ords = [int(value) for value in matches]

        if min(ords) <= 0:
            raise ValueError("cloze ordinal must start from 1")

        # 允许一张卡多个空：多个 c1 是合法的
        # 也允许多张卡：c1, c2, c3 是合法的
import json

from coreengine.ai_card_factory.provider import GeneratedCardDraft


def build_card_revision_system_prompt() -> str:
    return """
You are an AI flashcard draft editor.

Your job:
- Revise existing note drafts according to the user's instruction.
- Keep the number of drafts exactly the same as the input drafts.
- Return revised note drafts only.
- Do not create database cards.

Supported note types:
1. Basic: fields = [front, back]
2. Basic Reverse: fields = [front, back]
3. Cloze: fields = [cloze_text, extra]

Cloze rules:
- Use {{c1::answer}} syntax.
- Multiple {{c1::...}} blanks appear on one card.
- Different ordinals such as {{c1::...}} and {{c2::...}} create different cards.
""".strip()


def build_card_revision_user_prompt(
    current_drafts: list[GeneratedCardDraft],
    user_instruction: str,
    language: str,
) -> str:
    drafts_payload = [
        {
            "note_type_id": draft.note_type_id,
            "fields": draft.fields,
            "tags": draft.tags,
            "hint": draft.hint,
            "reason": draft.reason,
        }
        for draft in current_drafts
    ]

    return f"""
Language: {language}

User revision instruction:
{user_instruction}

Current drafts:
{json.dumps(drafts_payload, ensure_ascii=False, indent=2)}

Return the same number of drafts, revised according to the instruction.
""".strip()
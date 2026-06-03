from coreengine.ai_card_factory.provider import GeneratedCardDraft


class FakeCardDraftProvider:
    def generate_drafts(
        self,
        source_text: str,
        user_prompt: str,
        note_type_id: int | None,
        max_cards: int,
        language: str,
    ) -> list[GeneratedCardDraft]:
        target_note_type_id = note_type_id or 1

        if target_note_type_id == 3:
            return [
                GeneratedCardDraft(
                    note_type_id=3,
                    fields=[
                        "光合作用发生在 {{c1::叶绿体}}，需要 {{c1::光能}}、{{c1::水}} 和 {{c1::二氧化碳}}。",
                        "AI generated cloze example",
                    ],
                    tags=["ai-generated"],
                    hint="photosynthesis",
                    reason="Generated as a same-ordinal multi-blank cloze card.",
                )
            ]

        return [
            GeneratedCardDraft(
                note_type_id=1,
                fields=[
                    "What is the main idea of the source text?",
                    source_text.strip()[:300],
                ],
                tags=["ai-generated"],
                hint="AI generated",
                reason="Generated from source text.",
            )
        ]

    def revise_drafts(
        self,
        current_drafts: list[GeneratedCardDraft],
        user_instruction: str,
        language: str,
    ) -> list[GeneratedCardDraft]:
        revised: list[GeneratedCardDraft] = []

        for draft in current_drafts:
            revised.append(
                GeneratedCardDraft(
                    note_type_id=draft.note_type_id,
                    fields=draft.fields,
                    tags=list(dict.fromkeys([*draft.tags, "revised"])),
                    hint=draft.hint,
                    reason=f"Revised by instruction: {user_instruction}",
                )
            )

        return revised
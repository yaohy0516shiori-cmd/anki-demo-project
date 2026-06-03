from contextlib import nullcontext

from coreengine.ai_card_factory.models import (
    CardDraftBatch,
    CardDraftItem,
    CardDraftVersion,
)
from coreengine.ai_card_factory.provider import GeneratedCardDraft
from coreengine.ai_card_factory.validator import CardDraftValidator
from coreengine.note_type.type_registry import get_note_type


class AICardFactoryService:
    def __init__(
        self,
        draft_repo,
        draft_provider,
        note_service,
        deck_repo,
        transaction_manager=None,
    ):
        self.__draft_repo = draft_repo
        self.__draft_provider = draft_provider
        self.__note_service = note_service
        self.__deck_repo = deck_repo
        self.__validator = CardDraftValidator()
        self.__transaction_manager = transaction_manager

    def __transaction(self):
        if self.__transaction_manager is None:
            return nullcontext()
        return self.__transaction_manager.transaction()

    def generate_drafts(
        self,
        user_id: int,
        source_text: str,
        user_prompt: str = "",
        deck_id: int | None = None,
        note_type_id: int | None = None,
        max_cards: int = 10,
        language: str = "zh",
    ):
        self.__validate_common_input(user_id, source_text, deck_id, max_cards)

        generated = self.__draft_provider.generate_drafts(
            source_text=source_text,
            user_prompt=user_prompt,
            note_type_id=note_type_id,
            max_cards=max_cards,
            language=language,
        )

        if not generated:
            raise ValueError("AI did not generate any card drafts")

        for draft in generated:
            self.__validator.validate_generated_draft(draft)

        with self.__transaction():
            batch = self.__draft_repo.create_batch(
                CardDraftBatch(
                    batch_id=None,
                    user_id=user_id,
                    deck_id=deck_id,
                    source_type="text",
                    source_text=source_text,
                    user_prompt=user_prompt,
                    status="pending",
                )
            )

            for draft in generated:
                item = self.__draft_repo.create_item(
                    CardDraftItem(
                        item_id=None,
                        batch_id=batch.batch_id,
                        user_id=user_id,
                        note_type_id=draft.note_type_id,
                        status="pending",
                    )
                )

                self.__draft_repo.create_version(
                    CardDraftVersion(
                        version_id=None,
                        item_id=item.item_id,
                        user_id=user_id,
                        version_no=1,
                        fields=draft.fields,
                        tags=draft.tags,
                        hint=draft.hint,
                        reason=draft.reason,
                        user_instruction=user_prompt,
                        created_by="ai",
                    )
                )

        return self.get_batch(user_id, batch.batch_id)

    def revise_drafts(
        self,
        user_id: int,
        batch_id: int,
        user_instruction: str,
        language: str = "zh",
    ):
        batch = self.__draft_repo.get_batch(user_id, batch_id)

        if batch.status != "pending":
            raise ValueError("Only pending draft batches can be revised")

        current = self.__draft_repo.get_items_with_latest_versions(user_id, batch_id)

        provider_input = [
            GeneratedCardDraft(
                note_type_id=row.item.note_type_id,
                fields=row.latest_version.fields,
                tags=row.latest_version.tags,
                hint=row.latest_version.hint,
                reason=row.latest_version.reason,
            )
            for row in current
            if row.item.status == "pending"
        ]

        revised = self.__draft_provider.revise_drafts(
            current_drafts=provider_input,
            user_instruction=user_instruction,
            language=language,
        )

        if len(revised) != len(provider_input):
            raise ValueError("Revised draft count does not match current draft count")

        for draft in revised:
            self.__validator.validate_generated_draft(draft)

        pending_items = [row for row in current if row.item.status == "pending"]

        with self.__transaction():
            for row, draft in zip(pending_items, revised):
                next_version_no = self.__draft_repo.get_next_version_no(
                    user_id,
                    row.item.item_id,
                )

                self.__draft_repo.create_version(
                    CardDraftVersion(
                        version_id=None,
                        item_id=row.item.item_id,
                        user_id=user_id,
                        version_no=next_version_no,
                        fields=draft.fields,
                        tags=draft.tags,
                        hint=draft.hint,
                        reason=draft.reason,
                        user_instruction=user_instruction,
                        created_by="ai",
                    )
                )

        return self.get_batch(user_id, batch_id)

    def confirm_drafts(
        self,
        user_id: int,
        batch_id: int,
        accepted_item_ids: list[int],
        rejected_item_ids: list[int] | None = None,
        today=None,
    ):
        batch = self.__draft_repo.get_batch(user_id, batch_id)

        if batch.status != "pending":
            raise ValueError("Only pending draft batches can be confirmed")

        if not accepted_item_ids:
            raise ValueError("accepted_item_ids cannot be empty")

        rejected_item_ids = rejected_item_ids or []
        all_rows = self.__draft_repo.get_items_with_latest_versions(user_id, batch_id)
        rows_by_id = {row.item.item_id: row for row in all_rows}

        created_note_ids: list[int] = []

        with self.__transaction():
            for item_id in rejected_item_ids:
                if item_id not in rows_by_id:
                    raise ValueError(f"Draft item {item_id} not found")
                self.__draft_repo.mark_item_rejected(user_id, item_id)

            for item_id in accepted_item_ids:
                row = rows_by_id.get(item_id)
                if row is None:
                    raise ValueError(f"Draft item {item_id} not found")

                if row.item.status != "pending":
                    raise ValueError(f"Draft item {item_id} is not pending")

                latest = row.latest_version
                note_type = get_note_type(row.item.note_type_id)

                note_id = self.__note_service.create_note(
                    user_id=user_id,
                    note_type=note_type,
                    fields=latest.fields,
                    tags=latest.tags,
                    hint=latest.hint,
                    deck_id=batch.deck_id,
                    today=today,
                )

                self.__draft_repo.mark_item_created(user_id, item_id, note_id)
                created_note_ids.append(note_id)

            self.__draft_repo.mark_batch_confirmed(user_id, batch_id)

        return {
            "batch_id": batch_id,
            "created_note_ids": created_note_ids,
            "created_note_count": len(created_note_ids),
        }

    def discard_batch(self, user_id: int, batch_id: int):
        batch = self.__draft_repo.get_batch(user_id, batch_id)

        if batch.status != "pending":
            raise ValueError("Only pending draft batches can be discarded")

        with self.__transaction():
            self.__draft_repo.mark_batch_discarded(user_id, batch_id)

        return {"batch_id": batch_id, "status": "discarded"}

    def get_batch(self, user_id: int, batch_id: int):
        batch = self.__draft_repo.get_batch(user_id, batch_id)
        items = self.__draft_repo.get_items_with_latest_versions(user_id, batch_id)

        return {
            "batch": batch,
            "items": items,
        }

    def __validate_common_input(
        self,
        user_id: int,
        source_text: str,
        deck_id: int | None,
        max_cards: int,
    ) -> None:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User id must be a positive integer")

        if not isinstance(source_text, str) or not source_text.strip():
            raise ValueError("source_text cannot be empty")

        if not isinstance(max_cards, int) or max_cards <= 0 or max_cards > 30:
            raise ValueError("max_cards must be between 1 and 30")

        if deck_id is not None:
            if not isinstance(deck_id, int) or deck_id <= 0:
                raise ValueError("Deck id must be a positive integer")
            self.__deck_repo.get_deck(user_id, deck_id)
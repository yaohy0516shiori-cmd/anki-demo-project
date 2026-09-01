from typing import Protocol

from coreengine.ai_card_factory.models import (
    CardDraftBatch,
    CardDraftItem,
    CardDraftVersion,
    CardDraftWithLatestVersion,
)


class CardDraftRepository(Protocol):
    def create_batch(self, batch: CardDraftBatch) -> CardDraftBatch:
        ...

    def create_item(self, item: CardDraftItem) -> CardDraftItem:
        ...

    def create_version(self, version: CardDraftVersion) -> CardDraftVersion:
        ...

    def get_batch(self, user_id: int, batch_id: int) -> CardDraftBatch:
        ...

    def get_items_with_latest_versions(
        self,
        user_id: int,
        batch_id: int,
    ) -> list[CardDraftWithLatestVersion]:
        ...

    def get_latest_version(self, user_id: int, item_id: int) -> CardDraftVersion:
        ...

    def mark_item_created(
        self,
        user_id: int,
        item_id: int,
        note_id: int,
    ) -> None:
        ...

    def mark_item_rejected(
        self,
        user_id: int,
        item_id: int,
    ) -> None:
        ...

    def mark_batch_confirmed(
        self,
        user_id: int,
        batch_id: int,
    ) -> None:
        ...

    def mark_batch_discarded(
        self,
        user_id: int,
        batch_id: int,
    ) -> None:
        ...
    
    def get_next_version_no(self, user_id: int, item_id: int) -> int:
        ...
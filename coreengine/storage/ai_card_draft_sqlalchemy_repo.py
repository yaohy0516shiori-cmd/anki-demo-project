from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from coreengine.ai_card_factory.models import (
    CardDraftBatch,
    CardDraftItem,
    CardDraftVersion,
    CardDraftWithLatestVersion,
)
from coreengine.storage.sqlalchemy_models import (
    AICardDraftBatchORM,
    AICardDraftItemORM,
    AICardDraftVersionORM,
    utc_now,
)


class SqlAlchemyCardDraftRepository:
    def __init__(self, db: DbSession):
        self.__db = db

    def __batch_to_domain(self, orm: AICardDraftBatchORM) -> CardDraftBatch:
        return CardDraftBatch(
            batch_id=orm.batch_id,
            user_id=orm.user_id,
            deck_id=orm.deck_id,
            source_type=orm.source_type,
            source_text=orm.source_text,
            user_prompt=orm.user_prompt,
            status=orm.status,
            created_at=orm.created_at.isoformat() if orm.created_at else None,
            updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        )

    def __item_to_domain(self, orm: AICardDraftItemORM) -> CardDraftItem:
        return CardDraftItem(
            item_id=orm.item_id,
            batch_id=orm.batch_id,
            user_id=orm.user_id,
            note_type_id=orm.note_type_id,
            status=orm.status,
            created_note_id=orm.created_note_id,
            error_message=orm.error_message or "",
            created_at=orm.created_at.isoformat() if orm.created_at else None,
            updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        )

    def __version_to_domain(self, orm: AICardDraftVersionORM) -> CardDraftVersion:
        return CardDraftVersion(
            version_id=orm.version_id,
            item_id=orm.item_id,
            user_id=orm.user_id,
            version_no=orm.version_no,
            fields=list(orm.fields_json or []),
            tags=list(orm.tags_json or []),
            hint=orm.hint or "",
            reason=orm.reason or "",
            user_instruction=orm.user_instruction or "",
            created_by=orm.created_by,
            created_at=orm.created_at.isoformat() if orm.created_at else None,
        )

    def create_batch(self, batch: CardDraftBatch) -> CardDraftBatch:
        orm = AICardDraftBatchORM(
            user_id=batch.user_id,
            deck_id=batch.deck_id,
            source_type=batch.source_type,
            source_text=batch.source_text,
            user_prompt=batch.user_prompt,
            status=batch.status,
        )
        self.__db.add(orm)
        self.__db.flush()
        return self.__batch_to_domain(orm)

    def create_item(self, item: CardDraftItem) -> CardDraftItem:
        orm = AICardDraftItemORM(
            batch_id=item.batch_id,
            user_id=item.user_id,
            note_type_id=item.note_type_id,
            status=item.status,
            created_note_id=item.created_note_id,
            error_message=item.error_message,
        )
        self.__db.add(orm)
        self.__db.flush()
        return self.__item_to_domain(orm)

    def create_version(self, version: CardDraftVersion) -> CardDraftVersion:
        orm = AICardDraftVersionORM(
            item_id=version.item_id,
            user_id=version.user_id,
            version_no=version.version_no,
            fields_json=version.fields,
            tags_json=version.tags,
            hint=version.hint,
            reason=version.reason,
            user_instruction=version.user_instruction,
            created_by=version.created_by,
        )
        self.__db.add(orm)
        self.__db.flush()
        return self.__version_to_domain(orm)

    def get_batch(self, user_id: int, batch_id: int) -> CardDraftBatch:
        stmt = select(AICardDraftBatchORM).where(
            AICardDraftBatchORM.user_id == user_id,
            AICardDraftBatchORM.batch_id == batch_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft batch not found")
        return self.__batch_to_domain(orm)

    def get_items_with_latest_versions(
        self,
        user_id: int,
        batch_id: int,
    ) -> list[CardDraftWithLatestVersion]:
        items_stmt = (
            select(AICardDraftItemORM)
            .where(
                AICardDraftItemORM.user_id == user_id,
                AICardDraftItemORM.batch_id == batch_id,
            )
            .order_by(AICardDraftItemORM.item_id)
        )
        item_orms = self.__db.execute(items_stmt).scalars().all()

        result: list[CardDraftWithLatestVersion] = []

        for item_orm in item_orms:
            version_stmt = (
                select(AICardDraftVersionORM)
                .where(
                    AICardDraftVersionORM.user_id == user_id,
                    AICardDraftVersionORM.item_id == item_orm.item_id,
                )
                .order_by(AICardDraftVersionORM.version_no.desc())
                .limit(1)
            )
            version_orm = self.__db.execute(version_stmt).scalar_one_or_none()
            if version_orm is None:
                raise ValueError("AI card draft version not found")

            result.append(
                CardDraftWithLatestVersion(
                    item=self.__item_to_domain(item_orm),
                    latest_version=self.__version_to_domain(version_orm),
                )
            )

        return result

    def get_latest_version(self, user_id: int, item_id: int) -> CardDraftVersion:
        stmt = (
            select(AICardDraftVersionORM)
            .where(
                AICardDraftVersionORM.user_id == user_id,
                AICardDraftVersionORM.item_id == item_id,
            )
            .order_by(AICardDraftVersionORM.version_no.desc())
            .limit(1)
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft version not found")
        return self.__version_to_domain(orm)

    def get_next_version_no(self, user_id: int, item_id: int) -> int:
        stmt = select(func.max(AICardDraftVersionORM.version_no)).where(
            AICardDraftVersionORM.user_id == user_id,
            AICardDraftVersionORM.item_id == item_id,
        )
        current = self.__db.execute(stmt).scalar_one()
        return int(current or 0) + 1

    def mark_item_created(self, user_id: int, item_id: int, note_id: int) -> None:
        stmt = select(AICardDraftItemORM).where(
            AICardDraftItemORM.user_id == user_id,
            AICardDraftItemORM.item_id == item_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft item not found")

        orm.status = "created"
        orm.created_note_id = note_id
        orm.updated_at = utc_now()
        self.__db.flush()

    def mark_item_rejected(self, user_id: int, item_id: int) -> None:
        stmt = select(AICardDraftItemORM).where(
            AICardDraftItemORM.user_id == user_id,
            AICardDraftItemORM.item_id == item_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft item not found")

        orm.status = "rejected"
        orm.updated_at = utc_now()
        self.__db.flush()

    def mark_batch_confirmed(self, user_id: int, batch_id: int) -> None:
        stmt = select(AICardDraftBatchORM).where(
            AICardDraftBatchORM.user_id == user_id,
            AICardDraftBatchORM.batch_id == batch_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft batch not found")

        orm.status = "confirmed"
        orm.updated_at = utc_now()
        self.__db.flush()

    def mark_batch_discarded(self, user_id: int, batch_id: int) -> None:
        stmt = select(AICardDraftBatchORM).where(
            AICardDraftBatchORM.user_id == user_id,
            AICardDraftBatchORM.batch_id == batch_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("AI card draft batch not found")

        orm.status = "discarded"
        orm.updated_at = utc_now()
        self.__db.flush()
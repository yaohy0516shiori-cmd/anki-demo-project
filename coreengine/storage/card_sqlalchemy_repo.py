from datetime import date

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session as DbSession

from coreengine.card.cardmodel import Card
from coreengine.card.card_repository import CardRepository
from coreengine.storage.sqlalchemy_models import CardORM


class SqlAlchemyCardRepository(CardRepository):
    def __init__(self, db: DbSession):
        self.__db = db

    def __to_domain(self, orm: CardORM) -> Card:
        return Card(
            user_id=orm.user_id,
            card_id=orm.card_id,
            note_id=orm.note_id,
            deck_id=orm.deck_id,
            template_ord=orm.template_ord,
            status=orm.status,
            due=orm.due,
            interval=orm.interval,
            ease=orm.ease,
            reps=orm.reps,
            lapses=orm.lapses,
            step_index=orm.step_index,
            created_at=orm.created_at.isoformat() if orm.created_at else None,
            updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        )

    def add_card(self, card: Card) -> Card:
        if card.card_id is not None:
            raise ValueError("Card ID must be None")

        orm = CardORM(
            user_id=card.user_id,
            note_id=card.note_id,
            deck_id=card.deck_id,
            template_ord=card.template_ord,
            status=card.status,
            due=card.due,
            interval=card.interval,
            ease=card.ease,
            reps=card.reps,
            lapses=card.lapses,
            step_index=card.step_index,
        )

        self.__db.add(orm)
        self.__db.flush()
        return self.get_card(card.user_id, orm.card_id)

    def get_card(self, user_id: int, card_id: int) -> Card:
        stmt = select(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.card_id == card_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Card not found")
        return self.__to_domain(orm)

    def update_card(self, user_id: int, card: Card) -> Card:
        stmt = select(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.card_id == card.card_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Card not found")

        orm.note_id = card.note_id
        orm.deck_id = card.deck_id
        orm.template_ord = card.template_ord
        orm.status = card.status
        orm.due = card.due
        orm.interval = card.interval
        orm.ease = card.ease
        orm.reps = card.reps
        orm.lapses = card.lapses
        orm.step_index = card.step_index

        self.__db.flush()
        return self.get_card(user_id, card.card_id)

    def get_cards_by_note_id(self, user_id: int, note_id: int) -> list[Card]:
        stmt = (
            select(CardORM)
            .where(CardORM.user_id == user_id, CardORM.note_id == note_id)
            .order_by(CardORM.note_id, CardORM.card_id, CardORM.template_ord)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def get_cards_by_note_id_and_ord(
        self,
        user_id: int,
        note_id: int,
        template_ord: int,
    ) -> Card | None:
        stmt = select(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.note_id == note_id,
            CardORM.template_ord == template_ord,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        return self.__to_domain(orm) if orm else None

    def get_cards_by_deck_id(self, user_id: int, deck_id: int) -> list[Card]:
        stmt = (
            select(CardORM)
            .where(CardORM.user_id == user_id, CardORM.deck_id == deck_id)
            .order_by(CardORM.card_id)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def get_due_cards_by_deck_id(
        self,
        user_id: int,
        deck_id: int,
        today: date,
    ) -> list[Card]:
        stmt = (
            select(CardORM)
            .where(
                CardORM.user_id == user_id,
                CardORM.deck_id == deck_id,
                CardORM.due <= today,
            )
            .order_by(CardORM.due, CardORM.card_id)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def list_cards(self, user_id: int) -> list[Card]:
        stmt = (
            select(CardORM)
            .where(CardORM.user_id == user_id)
            .order_by(CardORM.card_id)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def delete_card(self, user_id: int, card_id: int) -> None:
        stmt = select(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.card_id == card_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Card not found")

        self.__db.delete(orm)
        self.__db.flush()

    def delete_cards_by_note_id(self, user_id: int, note_id: int) -> int:
        stmt = delete(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.note_id == note_id,
        )
        result = self.__db.execute(stmt)
        self.__db.flush()
        return result.rowcount or 0

    def delete_cards_by_note_id_and_ord(
        self,
        user_id: int,
        note_id: int,
        template_ord: int,
    ) -> int:
        stmt = delete(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.note_id == note_id,
            CardORM.template_ord == template_ord,
        )
        result = self.__db.execute(stmt)
        self.__db.flush()
        return result.rowcount or 0

    def delete_cards_by_deck_id(self, user_id: int, deck_id: int) -> int:
        stmt = delete(CardORM).where(
            CardORM.user_id == user_id,
            CardORM.deck_id == deck_id,
        )
        result = self.__db.execute(stmt)
        self.__db.flush()
        return result.rowcount or 0

    def move_cards_to_deck(
        self,
        user_id: int,
        from_deck_id: int,
        to_deck_id: int,
    ) -> int:
        stmt = (
            update(CardORM)
            .where(
                CardORM.user_id == user_id,
                CardORM.deck_id == from_deck_id,
            )
            .values(deck_id=to_deck_id)
        )
        result = self.__db.execute(stmt)
        self.__db.flush()
        return result.rowcount or 0

    def move_note_cards_to_deck(
        self,
        user_id: int,
        note_id: int,
        deck_id: int,
    ) -> int:
        stmt = (
            update(CardORM)
            .where(
                CardORM.user_id == user_id,
                CardORM.note_id == note_id,
            )
            .values(deck_id=deck_id)
        )
        result = self.__db.execute(stmt)
        self.__db.flush()
        return result.rowcount or 0

    def count_cards(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(CardORM).where(CardORM.user_id == user_id)
        return self.__db.execute(stmt).scalar_one()
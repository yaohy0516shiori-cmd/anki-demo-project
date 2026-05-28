from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from coreengine.deck.deckmodel import Deck
from coreengine.deck.deck_repository import DeckRepository
from coreengine.storage.sqlalchemy_models import DeckORM


class SqlAlchemyDeckRepository(DeckRepository):
    def __init__(self, db: DbSession):
        self.__db = db

    def __to_domain(self, orm: DeckORM) -> Deck:
        return Deck(
            user_id=orm.user_id,
            deck_id=orm.deck_id,
            deck_name=orm.deck_name,
            deck_description=orm.deck_description,
            is_default=orm.is_default,
            created_at=orm.created_at.isoformat() if orm.created_at else None,
            updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        )

    def create_deck(self, deck: Deck) -> Deck:
        if deck.deck_id is not None:
            raise ValueError("Deck ID must be None")

        orm = DeckORM(
            user_id=deck.user_id,
            deck_name=deck.deck_name,
            deck_description=deck.deck_description or "",
            is_default=deck.is_default,
        )

        try:
            self.__db.add(orm)
            self.__db.flush()
        except IntegrityError as exc:
            raise ValueError("Deck already exists") from exc

        return self.get_deck(deck.user_id, orm.deck_id)

    def get_deck(self, user_id: int, deck_id: int) -> Deck:
        stmt = select(DeckORM).where(
            DeckORM.user_id == user_id,
            DeckORM.deck_id == deck_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Deck not found")
        return self.__to_domain(orm)

    def update_deck(self, user_id: int, deck: Deck) -> Deck:
        stmt = select(DeckORM).where(
            DeckORM.user_id == user_id,
            DeckORM.deck_id == deck.deck_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Deck not found")

        orm.deck_name = deck.deck_name
        orm.deck_description = deck.deck_description or ""
        self.__db.flush()
        return self.get_deck(user_id, deck.deck_id)

    def delete_deck(self, user_id: int, deck_id: int) -> None:
        if self.is_default_deck(user_id, deck_id):
            raise ValueError("Default deck cannot be deleted")

        stmt = select(DeckORM).where(
            DeckORM.user_id == user_id,
            DeckORM.deck_id == deck_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Deck not found")

        self.__db.delete(orm)
        self.__db.flush()

    def get_all_decks(self, user_id: int) -> list[Deck]:
        stmt = (
            select(DeckORM)
            .where(DeckORM.user_id == user_id)
            .order_by(DeckORM.deck_id)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def get_all_decks_ids(self, user_id: int) -> list[int]:
        stmt = select(DeckORM.deck_id).where(DeckORM.user_id == user_id)
        return list(self.__db.execute(stmt).scalars().all())

    def get_default_deck(self, user_id: int) -> Deck:
        return self.__ensure_default_deck(user_id)

    def get_default_deck_id(self, user_id: int) -> int:
        return self.__ensure_default_deck(user_id).deck_id

    def is_default_deck(self, user_id: int, deck_id: int) -> bool:
        return deck_id == self.get_default_deck_id(user_id)

    def clear_decks(self, user_id: int) -> None:
        rows = self.__db.execute(
            select(DeckORM).where(DeckORM.user_id == user_id)
        ).scalars().all()

        for row in rows:
            self.__db.delete(row)

        self.__db.flush()
        self.__ensure_default_deck(user_id)

    def get_deck_by_name(self, user_id: int, deck_name: str) -> Deck:
        stmt = select(DeckORM).where(
            DeckORM.user_id == user_id,
            DeckORM.deck_name == deck_name,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Deck not found")
        return self.__to_domain(orm)

    def ensure_created(self, user_id: int) -> Deck:
        return self.__ensure_default_deck(user_id)

    def __ensure_default_deck(self, user_id: int) -> Deck:
        stmt = select(DeckORM).where(
            DeckORM.user_id == user_id,
            DeckORM.is_default.is_(True),
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()

        if orm is not None:
            return self.__to_domain(orm)

        orm = DeckORM(
            user_id=user_id,
            deck_name="Default",
            deck_description="System default deck",
            is_default=True,
        )

        self.__db.add(orm)
        self.__db.flush()
        return self.__to_domain(orm)
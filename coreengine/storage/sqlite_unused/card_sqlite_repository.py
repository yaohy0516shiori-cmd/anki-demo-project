import sqlite3
from datetime import date

from ..card.cardmodel import Card
from ..card.card_repository import CardRepository


class SqliteCardRepository(CardRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.__conn = conn

    def __serialize_card(self, card: Card) -> dict:
        return {
            "user_id": card.user_id,
            "deck_id": card.deck_id,
            "note_id": card.note_id,
            "template_ord": card.template_ord,
            "status": card.status,
            "due": card.due.isoformat() if hasattr(card.due, "isoformat") else card.due,
            "interval": card.interval,
            "ease": card.ease,
            "reps": card.reps,
            "lapses": card.lapses,
            "step_index": card.step_index,
            "created_at": card.created_at,
            "updated_at": card.updated_at,
        }

    def __deserialize_card(self, row: sqlite3.Row) -> Card:
        return Card(
            user_id=row["user_id"],
            card_id=row["card_id"],
            note_id=row["note_id"],
            deck_id=row["deck_id"],
            template_ord=row["template_ord"],
            status=row["status"],
            due=date.fromisoformat(row["due"]),
            interval=int(row["interval"]),
            ease=row["ease"],
            reps=int(row["reps"]),
            lapses=int(row["lapses"]),
            step_index=int(row["step_index"]) if row["step_index"] is not None else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add_card(self, card: Card):
        if card.card_id is not None:
            raise ValueError("Card ID must be None")

        if card.note_id is None:
            raise ValueError("Note ID is required")

        data = self.__serialize_card(card)

        cursor = self.__conn.execute("""
        INSERT INTO card (
            user_id,
            note_id,
            deck_id,
            template_ord,
            status,
            due,
            interval,
            ease,
            reps,
            lapses,
            step_index,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["user_id"],
            data["note_id"],
            data["deck_id"],
            data["template_ord"],
            data["status"],
            data["due"],
            data["interval"],
            data["ease"],
            data["reps"],
            data["lapses"],
            data["step_index"],
            data["created_at"],
            data["updated_at"],
        ))

        return self.get_card(card.user_id, cursor.lastrowid)

    def get_card(self, user_id: int, card_id: int) -> Card:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("Card ID must be a positive integer")

        row = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ? AND card_id = ?
        """, (user_id, card_id)).fetchone()

        if row is None:
            raise ValueError("Card not found")

        return self.__deserialize_card(row)

    def update_card(self, user_id:int, card: Card):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if card.card_id is None:
            raise ValueError("Card ID is required")

        data = self.__serialize_card(card)

        cursor = self.__conn.execute("""
        UPDATE card SET
            note_id = ?,
            deck_id = ?,
            template_ord = ?,
            status = ?,
            due = ?,
            interval = ?,
            ease = ?,
            reps = ?,
            lapses = ?,
            step_index = ?,
            updated_at = ?
        WHERE user_id = ? AND card_id = ?
        """,
        (
            data["note_id"],
            data["deck_id"],
            data["template_ord"],
            data["status"],
            data["due"],
            data["interval"],
            data["ease"],
            data["reps"],
            data["lapses"],
            data["step_index"],
            data["updated_at"],
            user_id,
            card.card_id,
        ))

        if cursor.rowcount == 0:
            raise ValueError("Card not found")

        return self.get_card(user_id, card.card_id)

    def get_cards_by_note_id(self, user_id: int, note_id: int) -> list[Card]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        rows = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ? AND note_id = ?
        ORDER BY note_id, card_id, template_ord
        """, (user_id, note_id)).fetchall()

        return [self.__deserialize_card(row) for row in rows]

    def get_cards_by_note_id_and_ord(
        self,
        user_id: int,
        note_id: int,
        template_ord: int,
    ) -> Card | None:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        if not isinstance(template_ord, int) or template_ord < 0:
            raise ValueError("Template ord must be a non-negative integer")

        row = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ? AND note_id = ? AND template_ord = ?
        """, (user_id, note_id, template_ord)).fetchone()

        if row is None:
            return None

        return self.__deserialize_card(row)

    def list_cards(self, user_id: int) -> list[Card]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        rows = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ?
        ORDER BY card_id
        """, (user_id,)).fetchall()

        return [self.__deserialize_card(row) for row in rows]

    def delete_cards_by_note_id(self, user_id: int, note_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        cursor = self.__conn.execute("""
        DELETE FROM card
        WHERE user_id = ? AND note_id = ?
        """, (user_id, note_id))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def delete_cards_by_note_id_and_ord(
        self,
        user_id: int,
        note_id: int,
        template_ord: int,
    ) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        if not isinstance(template_ord, int) or template_ord < 0:
            raise ValueError("Template ord must be a non-negative integer")

        cursor = self.__conn.execute("""
        DELETE FROM card
        WHERE user_id = ? AND note_id = ? AND template_ord = ?
        """, (user_id, note_id, template_ord))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def delete_card(self, user_id: int, card_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(card_id, int) or card_id <= 0:
            raise ValueError("Card ID must be a positive integer")

        cursor = self.__conn.execute("""
        DELETE FROM card
        WHERE user_id = ? AND card_id = ?
        """, (user_id, card_id))

        if cursor.rowcount == 0:
            raise ValueError("Card not found")

        return cursor.rowcount

    def get_cards_by_deck_id(self, user_id: int, deck_id: int) -> list[Card]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        rows = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ? AND deck_id = ?
        ORDER BY deck_id, card_id, template_ord
        """, (user_id, deck_id)).fetchall()

        return [self.__deserialize_card(row) for row in rows]

    def get_due_cards_by_deck_id(self, user_id: int, deck_id: int, today: date) -> list[Card]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        rows = self.__conn.execute("""
        SELECT * FROM card
        WHERE user_id = ?
          AND deck_id = ?
          AND due <= ?
        ORDER BY due, note_id, card_id, template_ord
        """, (user_id, deck_id, today.isoformat())).fetchall()

        return [self.__deserialize_card(row) for row in rows]

    def move_note_cards_to_deck(self, user_id: int, note_id: int, deck_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        cursor = self.__conn.execute("""
        UPDATE card
        SET deck_id = ?
        WHERE user_id = ? AND note_id = ? AND deck_id != ?
        """, (deck_id, user_id, note_id, deck_id))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def move_cards_to_deck(self, user_id: int, from_deck_id: int, to_deck_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(from_deck_id, int) or from_deck_id <= 0:
            raise ValueError("From Deck ID must be a positive integer")

        if not isinstance(to_deck_id, int) or to_deck_id <= 0:
            raise ValueError("To Deck ID must be a positive integer")

        if from_deck_id == to_deck_id:
            return 0

        cursor = self.__conn.execute("""
        UPDATE card
        SET deck_id = ?
        WHERE user_id = ? AND deck_id = ?
        """, (to_deck_id, user_id, from_deck_id))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def delete_cards_by_deck_id(self, user_id: int, deck_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        cursor = self.__conn.execute("""
        DELETE FROM card
        WHERE user_id = ? AND deck_id = ?
        """, (user_id, deck_id))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def clear_cards(self, user_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        cursor = self.__conn.execute("""
        DELETE FROM card
        WHERE user_id = ?
        """, (user_id,))

        return cursor.rowcount if cursor.rowcount is not None else 0

    def count_cards(self, user_id: int) -> int:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        row = self.__conn.execute("""
        SELECT COUNT(*) FROM card
        WHERE user_id = ?
        """, (user_id,)).fetchone()

        return row[0]
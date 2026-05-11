from ..note.notemodels import Note
from .cardmodel import Card
from datetime import datetime, timezone, date
from ..note_type.type_registry import get_note_type
import re


class CardService:
    def __init__(self, card_repo, note_repo, deck_repo):
        self.card_repo = card_repo
        self.note_repo = note_repo
        self.deck_repo = deck_repo

    def create_cards_from_note(self, user_id: int, note: Note, deck_id: int, today=None):
        if note.note_id is None:
            raise ValueError("Note id is required")

        if note.user_id != user_id:
            raise ValueError("Note does not belong to this user")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")
        deck=self.deck_repo.get_deck(user_id, deck_id)
        if deck is None:
            raise ValueError("Deck not found")
        created_cards = []
        default_today = today if today is not None else datetime.now(timezone.utc).date()
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        for template_ord in self.__get_template_ords(note):
            card = Card(
                user_id=user_id,
                note_id=note.note_id,
                template_ord=template_ord,
                deck_id=deck_id,
                status="new",
                due=default_today,
                created_at=now,
                updated_at=now,
            )
            created_cards.append(self.card_repo.add_card(card))

        return created_cards

    def get_card(self, user_id: int, card_id: int):
        return self.card_repo.get_card(user_id, card_id)

    def get_cards_by_note_id(self, user_id: int, note_id: int):
        return self.card_repo.get_cards_by_note_id(user_id, note_id)

    def get_cards_by_deck_id(self, user_id: int, deck_id: int):
        return self.card_repo.get_cards_by_deck_id(user_id, deck_id)

    def get_due_cards_by_deck_id(self, user_id: int, deck_id: int, today: date):
        return self.card_repo.get_due_cards_by_deck_id(user_id, deck_id, today)

    def update_card(self, user_id: int, card: Card):
        if card.user_id != user_id:
            raise ValueError("User ID does not match")
        return self.card_repo.update_card(user_id, card)

    def get_template_ords(self, note: Note):
        return self.__get_template_ords(note)

    def delete_cards_by_note_id(self, user_id: int, note_id: int):
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note id must be a positive integer")

        deleted_count = self.card_repo.delete_cards_by_note_id(user_id, note_id)

        return {
            "message": f"deleted {deleted_count} cards for note {note_id}",
            "note_id": note_id,
            "deleted_card_count": deleted_count,
        }

    def delete_cards_by_deck_id(self, user_id: int, deck_id: int):
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")

        deleted_count = self.card_repo.delete_cards_by_deck_id(user_id, deck_id)

        return {
            "message": f"deleted {deleted_count} cards from deck {deck_id}",
            "deck_id": deck_id,
            "deleted_card_count": deleted_count,
        }

    def move_note_cards_to_deck(self, user_id: int, note_id: int, deck_id: int):
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note id must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")

        moved_count = self.card_repo.move_note_cards_to_deck(user_id, note_id, deck_id)

        return {
            "message": f"moved {moved_count} cards from note {note_id} to deck {deck_id}",
            "note_id": note_id,
            "deck_id": deck_id,
            "moved_card_count": moved_count,
        }

    def move_cards_to_deck(self, user_id: int, from_deck_id: int, to_deck_id: int):
        if not isinstance(from_deck_id, int) or from_deck_id <= 0:
            raise ValueError("From deck id must be a positive integer")

        if not isinstance(to_deck_id, int) or to_deck_id <= 0:
            raise ValueError("To deck id must be a positive integer")

        moved_count = self.card_repo.move_cards_to_deck(user_id, from_deck_id, to_deck_id)

        return {
            "message": f"moved {moved_count} cards from deck {from_deck_id} to deck {to_deck_id}",
            "from_deck_id": from_deck_id,
            "to_deck_id": to_deck_id,
            "moved_card_count": moved_count,
        }

    def reconcile_cards_for_note(self, user_id: int, note: Note, today=None, deck_id: int | None = None):
        if note.note_id is None:
            raise ValueError("Note id is required")

        if note.user_id != user_id:
            raise ValueError("Note does not belong to this user")

        expected_template_ords = self.__get_template_ords(note)
        expected_template_ords_set = set(expected_template_ords)

        existing_cards = self.get_cards_by_note_id(user_id, note.note_id)
        existing_by_ord = {card.template_ord: card for card in existing_cards}

        if existing_cards:
            target_deck_id = existing_cards[0].deck_id
        elif deck_id is not None:
            target_deck_id = deck_id
        elif expected_template_ords:
            raise ValueError("Deck id is required when reconciling a note without existing cards")
        else:
            target_deck_id = None

        for card in existing_cards:
            if card.template_ord not in expected_template_ords_set:
                self.card_repo.delete_card(user_id, card.card_id)

        default_today = today if today is not None else datetime.now(timezone.utc).date()
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        for template_ord in expected_template_ords:
            if template_ord in existing_by_ord:
                continue

            card = Card(
                user_id=user_id,
                note_id=note.note_id,
                template_ord=template_ord,
                deck_id=target_deck_id,
                status="new",
                due=default_today,
                created_at=now,
                updated_at=now,
            )
            self.card_repo.add_card(card)

        return self.get_cards_by_note_id(user_id, note.note_id)

    def __get_cloze_ords(self, text):
        ords = set()
        matches = re.findall(r"\{\{c(\d+)::.*?\}\}", text)

        for x in matches:
            ords.add(int(x) - 1)

        return sorted(ords)

    def __get_template_ords(self, note: Note):
        note_type = get_note_type(note.note_type_id)

        if note_type.kind == "basic":
            return [0]

        if note_type.kind == "cloze":
            return self.__get_cloze_ords(note.fields[0])

        if note_type.kind == "basic_reverse":
            return [0, 1]

        raise ValueError(f"Unsupported note type kind: {note_type.kind}")
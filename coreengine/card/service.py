from ..note.notemodels import Note
from .cardmodel import Card
from datetime import datetime, timezone, date
from ..note_type.type_registry import get_note_type
import re

# Generate cards from notes and provide card-level business interfaces.
class CardService:
    def __init__(self, card_repo,note_repo):
        self.card_repo = card_repo
        self.note_repo = note_repo

    def create_cards_from_note(self, note:Note, deck_id:int=1, today=None):
        # Decide how many cards to generate from a note and save them
        if note.note_id is None:
            raise ValueError("Note id is required")
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")
        create_cards = []
        default_today=today if today is not None else datetime.now(timezone.utc).date()
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for template_ord in self.__get_template_ords(note):
            card=Card(note_id=note.note_id, 
            template_ord=template_ord, 
            deck_id=deck_id,
            status='new',
            due=default_today,
            created_at=now,
            updated_at=now)
            create_cards.append(self.card_repo.add_card(card))
        return create_cards

    def get_card(self, card_id):
        # Read one card
        return self.card_repo.get_card(card_id)

    def get_cards_by_note_id(self, note_id):
        # Read all cards by note id
        return self.card_repo.get_cards_by_note_id(note_id)

    def get_cards_by_deck_id(self, deck_id:int):
        # Read all cards by deck id
        return self.card_repo.get_cards_by_deck_id(deck_id)

    def get_due_cards_by_deck_id(self, deck_id:int, today:date):
        # Read all cards that are due today
        return self.card_repo.get_due_cards_by_deck_id(deck_id, today)

    def update_card(self, card):
        # Update a card
        return self.card_repo.update_card(card)
    
    def get_template_ords(self, note:Note):
        # Get the template ordinals for a note
        # Public wrapper used by note/card synchronization flow
        return self.__get_template_ords(note)

    def delete_cards_by_note_id(self, note_id:int):
        # delete all cards generated from a note
        return self.card_repo.delete_cards_by_note_id(note_id)

    def move_note_cards_to_deck(self, note_id:int, deck_id:int) -> int:
        # Move all cards from a note to a deck
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note id must be a positive integer")
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")
        return self.card_repo.move_note_cards_to_deck(note_id, deck_id)
    
    def move_cards_to_deck(self, from_deck_id:int, to_deck_id:int) -> int:
        # Move all cards from a deck to a new deck
        if not isinstance(from_deck_id, int) or from_deck_id <= 0:
            raise ValueError("From deck id must be a positive integer")
        if not isinstance(to_deck_id, int) or to_deck_id <= 0:
            raise ValueError("To deck id must be a positive integer")
        return self.card_repo.move_cards_to_deck(from_deck_id, to_deck_id)

    def reconcile_cards_for_note(self, note:Note, today=None):
        # synchronize existing cards with current note fields
        if note.note_id is None:
            raise ValueError("Note id is required")
        
        expected_template_ords=self.__get_template_ords(note)
        expected_template_ords_set=set(expected_template_ords)

        existing_cards=self.get_cards_by_note_id(note.note_id)
        existing_by_ord={card.template_ord:card for card in existing_cards}
        target_deck_id = existing_cards[0].deck_id if existing_cards else 1

        for card in existing_cards:
            if card.template_ord not in expected_template_ords_set:
                self.card_repo.delete_card(card.card_id)
            
        default_today=today if today is not None else datetime.now(timezone.utc).date()
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        for template_ord in expected_template_ords:
            if template_ord in existing_by_ord:
                continue
            card=Card(
                note_id=note.note_id,
                template_ord=template_ord,
                deck_id=target_deck_id,
                status='new',
                due=default_today,
                created_at=now,
                updated_at=now
            )
            self.card_repo.add_card(card)

        return self.get_cards_by_note_id(note.note_id)
    

    def __get_cloze_ords(self, text):
        # Extract cloze ordinals from cloze text
        # if catch the whole string, use re.findall(r"\{\{c\d+::.*?\}\}", text), no parentheses
        ord=set()
        matches=re.findall(r"\{\{c(\d+)::.*?\}\}", text)
        for x in matches:
            ord.add(int(x)-1)
        return sorted(ord)

    def __get_template_ords(self, note:Note):
        # Decide which template ordinals should be generated
        note_type = get_note_type(note.note_type_id)
        if note_type.kind == "basic":
            return [0]
        elif note_type.kind == "cloze":
            return self.__get_cloze_ords(note.fields[0])
        elif note_type.kind == "basic_reverse":
            return [0, 1]
        else:
            raise ValueError(f"unsupported note type kind: {note_type.kind}")
    

    
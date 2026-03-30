from note_type.notetype import NoteType
from note.notemodels import Note
from card.cardmodel import Card
from datetime import datetime, timezone
from note_type.type_registry import get_note_type
import re
from card.repository import InMemoryCardRepository

class CardService:
    def __init__(self, card_repo:InMemoryCardRepository):
        self.card_repo = card_repo

    def create_cards_from_note(self, note:Note):
        if note.note_id is None:
            raise ValueError("Note id is required")
        create_cards = []
        today=datetime.now(timezone.utc).date()
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for template_ord in self.__get_template_ords(note):
            card=Card(note_id=note.note_id, 
            template_ord=template_ord, 
            status='new',
            due=today,
            created_at=now,
            updated_at=now)
            create_cards.append(self.card_repo.add_card(card))
        return create_cards

    def get_card(self, card_id):
        return self.card_repo.get_card(card_id)

    def get_card_by_note_id(self, note_id):
        return self.card_repo.get_card_by_note_id(note_id)

    def get_due_cards(self, today):
        result=[]
        for card in self.card_repo.list_cards():
            if card.due is not None and card.due <= today:
                result.append(card)
        return result

    def update_card(self, card):
        return self.card_repo.update_card(card)

    def __get_cloze_ords(self, text):
        # if catch the whole string, use re.findall(r"\{\{c\d+::.*?\}\}", text), no parentheses
        ord=set()
        matches=re.findall(r"\{\{c(\d+)::.*?\}\}", text)
        for x in matches:
            ord.add(int(x)-1)
        return sorted(ord)

    def __get_template_ords(self, note:Note):
        note_type = get_note_type(note.note_type_id)
        if note_type.kind == "basic":
            return [0]
        elif note_type.kind == "cloze":
            return self.__get_cloze_ords(note.fields[0])
        elif note_type.kind == "basic_reverse":
            return [0, 1]
        else:
            raise ValueError(f"unsupported note type kind: {note_type.kind}")
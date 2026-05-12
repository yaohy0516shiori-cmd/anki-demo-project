from datetime import datetime, timezone, date
from ..card.cardmodel import Card
from ..card.card_repository import CardRepository
from ..note.note_repository import NoteRepository
from ..deck.deck_repository import DeckRepository
from ..reviewlogger.service import ReviewLoggerService
from ..render.card_render import render_card, render_hint
from .session_repository import SessionRepository
from .session import Session
from contextlib import nullcontext

# Study session coordinator.
class StudyService:
    VALID_STATUSES={"new","learning","relearning","review"}

    # Inject repositories/services and initialize three queues
    def __init__(
        self,
        card_repo:CardRepository,
        review_service:ReviewLoggerService,
        note_repo:NoteRepository,
        deck_repo:DeckRepository,
        session_repo:SessionRepository,
        transaction_manager=None
        ):
        self.__card_repo=card_repo
        self.__note_repo=note_repo
        self.__review_service=review_service
        self.__deck_repo=deck_repo
        self.__session_repo=session_repo
        self.__transaction_manager=transaction_manager

    def __transaction(self):
        # used to manage the transaction
        if self.__transaction_manager is None:
            return nullcontext()
        return self.__transaction_manager.transaction()

    # Start a study session, filter today's eligible cards, and distribute them into queues
    def start_study_session(self,user_id:int,deck_id:int,today:date | None=None):
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")
        with self.__transaction():
            deck=self.__deck_repo.get_deck(user_id, deck_id)
            if deck is None:
                raise ValueError("Deck not found")
            resolved_today=self.__resolve_today(today)
            due_cards=self.__card_repo.get_due_cards_by_deck_id(user_id, deck_id, resolved_today) or []
            
            learning_cards=[]
            review_cards=[]
            new_cards=[]

            for card in due_cards:
                if card.status == "new":
                    new_cards.append(card)
                elif card.status in {"learning","relearning"} :
                    learning_cards.append(card)
                elif card.status == "review":
                    review_cards.append(card)
                
            learning_cards.sort(key=self.__queue_sort_key)
            review_cards.sort(key=self.__queue_sort_key)
            new_cards.sort(key=self.__queue_sort_key)

            session=Session.create(user_id, deck_id, resolved_today)
            session.learning_queue=[card.card_id for card in learning_cards]
            session.review_queue=[card.card_id for card in review_cards]
            session.new_queue=[card.card_id for card in new_cards]
            session=self.__session_repo.create_session(user_id, session)

        return {
            "user_id":user_id,
            "session_id":session.session_id,
            "deck_id":deck_id,
            "deck_name":deck.deck_name,
            "learning_queue":len(session.learning_queue),
            "review_queue":len(session.review_queue),
            "new_queue":len(session.new_queue),
        }

    # Resolve today's date, use today if provided, otherwise use current UTC date
    def __resolve_today(self,today:date | None=None):
        return today if today is not None else datetime.now(timezone.utc).date()

    # Pop the next card from session queues and render front/back
    def get_next_card(self, user_id:int, session_id: str):
        with self.__transaction():
            session = self.__get_session_or_raise(user_id, session_id)

            if session.current_card_id is not None:
                raise ValueError("Finish the current card before getting the next one")

            card_id = self.__pop_next_card_id(session)
            if card_id is None:
                return None

            session.current_card_id = card_id
            session.current_hint_used = False
            session.current_back_revealed = False
            self.__session_repo.update_session(user_id, session)

            card = self.__card_repo.get_card(user_id, card_id)
            note = self.__note_repo.get_note(user_id, card.note_id)
            if note is None:
                raise ValueError("Note not found")

            rendered = render_card(card, note)

            return {
                "user_id":user_id,
                "session_id": session.session_id,
                "card": {
                    "card_id": card.card_id,
                    "note_id": card.note_id,
                    "deck_id": card.deck_id,
                    "template_ord": card.template_ord,
                    "status": card.status,
                    "due": card.due.isoformat(),
                    "interval": card.interval,
                    "ease": card.ease,
                    "reps": card.reps,
                    "lapses": card.lapses,
                    "step_index": card.step_index,
                },
                "note": {
                    "note_id": note.note_id,
                    "note_type_id": note.note_type_id,
                    "fields": note.fields,
                    "tags": note.tags,
                    "hint": note.hint,
                    "sort_field": note.sort_field,
                    "checksum": note.checksum,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                },
                "front": rendered["front"],
                "status": card.status,
                "step_index": card.step_index,
                "deck_id": session.deck_id,
                "hint_available": bool(note.hint and note.hint.strip()),
            }
    
    # Submit rating for current card, call review service, and re-enqueue if needed
    def rate_current_card(self, user_id:int, session_id: str, rating: str):
        with self.__transaction():
            session = self.__get_session_or_raise(user_id, session_id)

            if session.current_card_id is None:
                raise ValueError("No current card to rate")

            result = self.__review_service.review_card(
                user_id,
                session.current_card_id,
                rating,
                today=session.today,
                hint_used=session.current_hint_used,
            )

            updated_card = result["card"]

            if self.__is_eligible(updated_card, session.today) and updated_card.deck_id == session.deck_id:
                self.__enqueue_card(session, updated_card.card_id, updated_card.status)

            session.current_card_id = None
            session.current_hint_used = False
            session.current_back_revealed = False
            self.__session_repo.update_session(user_id, session)

        return result

    def reveal_back_of_current_card(self, user_id:int, session_id: str):
        with self.__transaction():
            session = self.__get_session_or_raise(user_id, session_id)

            if session.current_card_id is None:
                raise ValueError("No current card to reveal")

            card = self.__card_repo.get_card(user_id, session.current_card_id)
            note = self.__note_repo.get_note(user_id, card.note_id)
            if note is None:
                raise ValueError("Note not found")

            session.current_back_revealed = True
            self.__session_repo.update_session(user_id, session)

            return render_card(card, note)["back"]

    def reveal_hint_of_current_card(self, user_id:int, session_id: str):
        with self.__transaction():
            session = self.__get_session_or_raise(user_id, session_id)

            if session.current_card_id is None:
                raise ValueError("No current card to reveal")
            if session.current_back_revealed:
                raise ValueError("Back of the current card has already been revealed")

            card = self.__card_repo.get_card(user_id, session.current_card_id)
            note = self.__note_repo.get_note(user_id, card.note_id)
            if note is None:
                raise ValueError("Note not found")

            hint_text = render_hint(note)
            if hint_text:
                session.current_hint_used = True
                self.__session_repo.update_session(user_id, session)
                return hint_text
            return ""

    # Check if the study session is finished
    def is_finished(self, user_id:int, session_id: str) -> bool:
        session = self.__get_session_or_raise(user_id, session_id)
        return (
            len(session.learning_queue) == 0
            and len(session.review_queue) == 0
            and len(session.new_queue) == 0
            and session.current_card_id is None
        )

    # Pop the next card from the session queues
    def __pop_next_card_id(self, session):
        if len(session.learning_queue) > 0:
            return session.learning_queue.pop(0)
        if len(session.review_queue) > 0:
            return session.review_queue.pop(0)
        if len(session.new_queue) > 0:
            return session.new_queue.pop(0)
        return None

    # Check if a card is eligible for the study session
    def __is_eligible(self, card: Card, today: date) -> bool:
        return card.status in self.VALID_STATUSES and card.due is not None and card.due <= today

    # Enqueue a card into the appropriate queue
    def __enqueue_card(self, session, card_id: int, status: str):
        if status == "new":
            session.new_queue.append(card_id)
        elif status in {"learning", "relearning"}:
            session.learning_queue.append(card_id)
        elif status == "review":
            session.review_queue.append(card_id)

    # Sort key for card queues
    def __queue_sort_key(self,card:Card):
        return (card.due,card.note_id,card.template_ord)
        
    def __get_session_or_raise(self, user_id:int, session_id: str):
        session = self.__session_repo.get_session(user_id, session_id)
        if session is None:
            raise ValueError("Session not found")
        return session

from collections import deque
from datetime import datetime,timezone,date
from ..card.cardmodel import Card
from ..storage.card_sqlite_repository import SqliteCardRepository
from ..reviewlogger.repository import ReviewLoggerRepository
from ..reviewlogger.service import ReviewLoggerService
from ..render.card_render import render_card, render_hint
from ..storage.note_sqlite_repository import SqliteNoteRepository
from ..storage.deck_sqlite_repository import SqliteDeckRepository

# Study session coordinator.
class StudyService:
    VALID_STATUSES={"new","learning","relearning","review"}

    # Inject repositories/services and initialize three queues
    def __init__(
        self,
        card_repo:SqliteCardRepository,
        review_service:ReviewLoggerService,
        note_repo:SqliteNoteRepository,
        deck_repo:SqliteDeckRepository
        ):
        self.__card_repo=card_repo
        self.__note_repo=note_repo
        self.__review_service=review_service
        self.__deck_repo=deck_repo

        self.__learning_queue=deque()
        self.__review_queue=deque()
        self.__new_queue=deque()

        self.__session_deck_id=None
        self.__current_card_id=None
        self.__current_hint_used=False
        self.__current_back_revealed=False
        self.__today=None

    # Start a study session, filter today's eligible cards, and distribute them into queues
    def start_study_session(self,deck_id:int,today:date | None=None):
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck id must be a positive integer")
        deck=self.__deck_repo.get_deck(deck_id)
        if deck is None:
            raise ValueError("Deck not found")
        self.__today=self.__resolve_today(today)
        self.__session_deck_id=deck_id
        self.__current_card_id=None
        self.__current_hint_used=False
        self.__current_back_revealed=False

        self.__learning_queue.clear()
        self.__review_queue.clear()
        self.__new_queue.clear()
        
        learning_cards=[]
        review_cards=[]
        new_cards=[]

        cards=self.__card_repo.get_due_cards_by_deck_id(self.__session_deck_id, self.__today)
        for card in cards:
            if card.status == "new":
                new_cards.append(card)
            elif card.status in {"learning","relearning"} :
                learning_cards.append(card)
            elif card.status == "review":
                review_cards.append(card)
            
        learning_cards.sort(key=self.__queue_sort_key)
        review_cards.sort(key=self.__queue_sort_key)
        new_cards.sort(key=self.__queue_sort_key)

        self.__learning_queue=deque(learning_cards)
        self.__review_queue=deque(review_cards)
        self.__new_queue=deque(new_cards)

        return {
            "deck_id":self.__session_deck_id,
            "deck_name":deck.deck_name,
            "learning_queue":len(self.__learning_queue),
            "review_queue":len(self.__review_queue),
            "new_queue":len(self.__new_queue),
        }

    # Resolve today's date, use today if provided, otherwise use current UTC date
    def __resolve_today(self,today:date | None=None):
        return today if today is not None else datetime.now(timezone.utc).date()

    # Pop the next card from session queues and render front/back
    def get_next_card(self):
        if self.__session_deck_id is None:
            raise ValueError("Session has not been started")
        if self.__current_card_id is not None:
            raise ValueError("Finish the current card before getting the next one")

        card=self.__pop_next_card()
        if card is None:
            return None
        self.__current_card_id=card.card_id
        note=self.__note_repo.get_note(card.note_id)
        if note is None:
            raise ValueError("Note not found")
        rendered=render_card(card,note)
        return {
            "card":card,
            "note":note,
            "front":rendered["front"],
            "status":card.status,
            "step_index":card.step_index,
            "deck_id":self.__session_deck_id,
            "hint_available":bool(note.hint and note.hint.strip()),
        }
    
    # Submit rating for current card, call review service, and re-enqueue if needed
    def rate_current_card(self,rating:str):
        self.__current_hint_used = False
        self.__current_back_revealed = False
        if self.__current_card_id is None:
            raise ValueError("No current card to rate")
        result=self.__review_service.review_card(
            self.__current_card_id,
            rating,
            today=self.__today,
            hint_used=self.__current_hint_used
            )

        updated_card=result["card"]

        if self.__is_eligible(updated_card) and updated_card.deck_id == self.__session_deck_id:
            self.__enqueue_card(updated_card)
        
        self.__current_card_id=None
        return result

    def reveal_back_of_current_card(self):
        if self.__current_card_id is None:
            raise ValueError("No current card to reveal")
        card=self.__card_repo.get_card(self.__current_card_id)
        if card is None:
            raise ValueError("Card not found")

        note=self.__note_repo.get_note(card.note_id)
        if note is None:
            raise ValueError("Note not found")

        self.__current_back_revealed=True
        return render_card(card,note)["back"]

    def reveal_hint_of_current_card(self):
        if self.__current_card_id is None:
            raise ValueError("No current card to reveal")
        if self.__current_back_revealed:
            raise ValueError("Back of the current card has already been revealed")

        card=self.__card_repo.get_card(self.__current_card_id)
        if card is None:
            raise ValueError("Card not found")

        note=self.__note_repo.get_note(card.note_id)
        if note is None:
            raise ValueError("Note not found")

        hint_text=render_hint(note)
        if hint_text:
            self.__current_hint_used=True
            return hint_text
        return ''

    # Check if the study session is finished
    def is_finished(self)->bool:
        return (len(self.__learning_queue) == 0 
            and len(self.__review_queue) == 0 
            and len(self.__new_queue) == 0
            and self.__current_card_id is None
            )

    # Pop the next card from the session queues
    def __pop_next_card(self):
        if len(self.__learning_queue) > 0:
            return self.__learning_queue.popleft()
        if len(self.__review_queue) > 0:
            return self.__review_queue.popleft()
        if len(self.__new_queue) > 0:
            return self.__new_queue.popleft()
        return None

    # Check if a card is eligible for the study session
    def __is_eligible(self,card:Card)->bool:
        return (card.status in self.VALID_STATUSES and card.due is not None and card.due <= self.__today)

    # Enqueue a card into the appropriate queue
    def __enqueue_card(self,card:Card):
        if card.status == "new":
            self.__new_queue.append(card)
        elif card.status in {"learning","relearning"}:
            self.__learning_queue.append(card)
        elif card.status == "review":
            self.__review_queue.append(card)

    # Sort key for card queues
    def __queue_sort_key(self,card:Card):
        return (card.due,card.note_id,card.template_ord)

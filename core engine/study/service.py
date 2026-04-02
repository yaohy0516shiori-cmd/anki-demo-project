from collections import deque
from datetime import datetime,timezone,date
from card.cardmodel import Card
from card.repository import InMemoryCardRepository
from reviewlogger.repository import ReviewLoggerRepository
from reviewlogger.service import ReviewLoggerService
from render.card_render import render_card
from note.repository import InMemoryNoteRepository

class StudyService:
    VALID_STATUSES={"new","learning","relearning","review"}
    def __init__(
        self,
        card_repo:InMemoryCardRepository,
        review_service:ReviewLoggerService,
        note_repo:InMemoryNoteRepository
        ):
        self.__card_repo=card_repo
        self.__note_repo=note_repo
        self.__review_service=review_service
        self.__learning_queue=deque()
        self.__review_queue=deque()
        self.__new_queue=deque()
        self.__current_card_id=None
        self.__today=None
        self.__is_active=False

    def start_study_session(self,today:date | None=None):
        self.__today=self.__resolve_today(today)
        self.__is_active=True
        self.__current_card_id=None
        self.__learning_queue.clear()
        self.__review_queue.clear()
        self.__new_queue.clear()
        
        learning_cards=[]
        review_cards=[]
        new_cards=[]

        for card in self.__card_repo.list_cards():
            if not self.__is_eligible(card):
                continue
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


    def __resolve_today(self,today:date | None=None):
        return today if today is not None else datetime.now(timezone.utc).date()

    def get_next_card(self):
        if not self.__is_active:
            raise ValueError("Study session is not active")
        if self.__current_card_id is None:
            raise ValueError("Current card has not been answered yet")

        card=self.__pop_next_card()
        if card is None:
            return None
        self.__current_card_id=card.card_id
        note=self.__note_repo.get_note(card.note_id)
        if note is None:
            raise ValueError("Note not found")
        rendered=render_card(card,note)
        # where is create card?
        return {
            "card":card,
            "note":note,
            "front":rendered["front"],
            "back":rendered["back"],
            "status":card.status,
            "step_index":card.step_index,
        }
    
    def answer_card(self,rating:str):
        if not self.__is_active:
            raise ValueError("Study session is not active")
        if self.__current_card_id is None:
            raise ValueError("Current card has not been answered yet")
        result=self.__review_service.review_card(self.__current_card_id,rating)
        updated_card=result["card"]

        if self.__is_eligible(updated_card):
            self.__enqueue_card(updated_card)
        
        self.__current_card_id=None
        return result

    def is_finished(self)->bool:
        if not self.__is_active:
            return True
        return (len(self.__learning_queue) == 0 
        and len(self.__review_queue) == 0 
        and len(self.__new_queue) == 0
        and self.__current_card_id is None
        )

    def __pop_next_card(self):
        if len(self.__learning_queue) > 0:
            return self.__learning_queue.popleft()
        if len(self.__review_queue) > 0:
            return self.__review_queue.popleft()
        if len(self.__new_queue) > 0:
            return self.__new_queue.popleft()
        return None

    def __is_eligible(self,card:Card)->bool:
        return (card.status in self.VALID_STATUSES and card.due is not None and card.due <= self.__today)

    def __enqueue_card(self,card:Card):
        if card.status == "new":
            self.__new_queue.append(card)
        elif card.status in {"learning","relearning"}:
            self.__learning_queue.append(card)
        elif card.status == "review":
            self.__review_queue.append(card)

    def __queue_sort_key(self,card:Card):
        return (card.due,card.note_id,card.template_ord)

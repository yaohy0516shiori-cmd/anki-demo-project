'''
cardmodel is a class that represents a card in the game.
'''
from datetime import datetime,timezone,date

class Card:
    select_status={'new','learning','review','relearning'}

    def __init__(
        self,
        note_id:int,
        template_ord:int,
        card_id:int | None=None,
        status:str='new',
        due: date | None=None,
        interval: int=0,
        ease: float=2.5,
        reps: int=0,
        lapses: int=0,
        step_index: int |None=None,
        created_at:str | None=None,
        updated_at:str | None=None
        ):
        # Initialize scheduling-related fields
        if note_id <=0:
            raise ValueError("Note id must be positive")
        if template_ord <0:
            raise ValueError("Temp ord must be positive")
        if status not in self.select_status:
            raise ValueError(f"status: {status}")
        if interval < 0:
            raise ValueError("Interval must be non-negative")
        if ease <= 0:
            raise ValueError("Ease factor must be greater than 0")
        if reps < 0:
            raise ValueError("Repes must be non-negative")
        if lapses < 0:
            raise ValueError("Lapses must be non-negative")
        
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        self.note_id=note_id
        self.template_ord=template_ord
        self.card_id=card_id
        self.status=status # new, learning, review, relearning
        self.due=due if due is not None else datetime.now(timezone.utc).date()
        self.interval=interval
        self.ease=ease
        self.reps=reps
        self.lapses=lapses
        self.step_index=step_index
        self.created_at=created_at if created_at is not None else now
        self.updated_at=updated_at if updated_at is not None else now
        
    def is_new(self):
        # check if the card is new
        return self.status=='new'
        
    def is_learning(self):
        # check if the card is learning
        return self.status=='learning'
        
    def is_review(self):
        # check if the card is review
        return self.status=='review'
        
    def is_relearning(self):
        # check if the card is relearning
        return self.status=='relearning'
        
    def is_due(self):
        # check if the card is due
        return self.due is not None and self.due <= datetime.now(timezone.utc).date()
        
    def touch(self):
        # update the updated time of the card
        self.updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
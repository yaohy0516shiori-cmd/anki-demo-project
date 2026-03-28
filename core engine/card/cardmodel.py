'''
cardmodel is a class that represents a card in the game.
it contains the following attributes:
which notes is it from?
Number of the card in the note
status of the card (due, new, learning, etc.)
when it should be reviewed next
how many times it has been reviewed
how many times it has been correct
how many times it has been incorrect
how many times it has been skipped
how many times it has been suspended
how many times it has been archived
how many times it has been deleted
how many times it has been restored
how many times it has been exported
how many times it has been imported
'''
from datetime import datetime,timezone 

class Card:
    select_status={'new','learning','review','relearning'}

    def __init__(
        self,
        note_id:int,
        template_ord:int,
        card_id:int | None=None,
        status:str='new',
        due: datetime | None=None,
        interval: int=0,
        ease: float=2.5,
        reps: int=0,
        lapses: int=0,
        created_at:datetime | None=None,
        updated_at:datetime | None=None
        ):
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
        self.status=status
        self.due=due if due is not None else datetime.now(timezone.utc).date()
        self.interval=interval
        self.ease=ease
        self.reps=reps
        self.lapses=lapses
        self.created_at=created_at if created_at is not None else now
        self.updated_at=updated_at if updated_at is not None else now
        
    def is_new(self):
        return self.status=='new'
        
    def is_learning(self):
        return self.status=='learning'
        
    def is_review(self):
        return self.status=='review'
        
    def is_relearning(self):
        return self.status=='relearning'
        
    def is_due(self):
        return self.due is not None and self.due < datetime.now(timezone.utc).date()
        
    def touch(self):
        self.updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
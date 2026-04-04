from datetime import datetime,timezone,date
from .utils import normalize_datetime_value
class ReviewLog:
    '''
    record complete review process for a card
    which includes:
    card/rating/what change after review
    '''
    view_rating=['good','again']

    # Construct one review log with old/new state and scheduling fields
    def __init__(
        self,
        card_id:int,
        rating:str,
        old_status:str,
        new_status:str,
        old_due:date | None=None,
        new_due:date | None=None,
        old_interval:int | None=None,
        new_interval:int | None=None,
        old_ease:float | None=None,
        new_ease:float | None=None,
        old_lapses:int|None=None,
        new_lapses:int|None=None,
        old_reps:int|None=None,
        new_reps:int|None=None,
        old_step_index:int|None=None,
        new_step_index:int|None=None,
        log_id:int|None=None,
        review_time:str|None=None,
        ):
        if card_id<=0:
            raise ValueError("Card id must be positive")
        if rating not in self.view_rating:
            raise ValueError("Invalid rating")
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        self.card_id=card_id
        self.rating=rating
        self.old_status=old_status
        self.new_status=new_status
        self.old_due=old_due
        self.new_due=new_due
        self.old_interval=old_interval
        self.new_interval=new_interval
        self.old_ease=old_ease
        self.new_ease=new_ease
        self.old_lapses=old_lapses
        self.new_lapses=new_lapses
        self.old_reps=old_reps
        self.new_reps=new_reps
        self.old_step_index=old_step_index
        self.new_step_index=new_step_index
        self.log_id=log_id
        self.review_time=normalize_datetime_value(review_time) if review_time else now
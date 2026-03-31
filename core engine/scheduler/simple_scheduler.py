from datetime import datetime, timedelta, timezone, date
from card.cardmodel import Card

class Scheduler_v1:
    """
    A very small v1 scheduler.

    It only decides:
    - next status
    - next due date
    - next interval
    - next ease
    - next reps
    - next lapses

    It does NOT save anything.
    It only returns the calculated result.
    """
    valid_ratings=["good","again"]
    def __init__(self):
        pass

    def schedule(self,card:Card,rating:str) -> dict:
        if rating not in self.valid_ratings:
            raise ValueError(f"Invalid rating: {rating}")
        
        today=datetime.now(timezone.utc).date()

        if card.status=="new":
            return self.__schedule_new_card(card,rating,today)
        elif card.status=="learning":
            return self.__schedule_learning_card(card,rating,today)
        elif card.status=="review":
            return self.__schedule_review_card(card,rating,today)
        elif card.status=="relearning":
            return self.__schedule_relearning_card(card,rating,today)
        else:
            raise ValueError(f"Invalid card status: {card.status}")
        
    def __schedule_new_card(self,card:Card,rating:str,today:date) -> dict:
        # first time exposur
        # good->learning
        # again->stay new
        if rating=="good":
            return {
                "status":"learning",
                "due":today,
                "interval":0,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
        elif rating=="again":
            return {
                "status":"new",
                "due":today, # why today?
                "interval":0,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
    
    def __schedule_learning_card(self,card:Card,rating:str,today:date) -> dict:
        # learning + good  -> enter review
        # learning + again -> stay learning
        if rating=="good":
            return {
                "status":"review",
                "due":today+timedelta(days=1),
                "interval":1,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
        elif rating=="again":
            return {
                "status":"learning",
                "due":today,
                "interval":0,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }

    
    def __schedule_review_card(self,card:Card,rating:str,today:date) -> dict:
        # review + good  -> stay review, increase interval
        # review + again -> enter relearning, count one lapse
        if rating=="good":
            base_interval=card.interval if card.interval>0 else 1

            # simple algorithm for interval increase
            new_interval=max(round(base_interval*card.ease),base_interval+1)

            return {
                "status":"review",
                "due":today+timedelta(days=new_interval),
                "interval":new_interval,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
        # why? 依据是什么？cardmodel里默认值不是2.5吗？ 而且cardmodel为什么允许ease输入而不是直接给定初始值
        new_ease=max(1.3, round(card.ease-0.2,2)) 

        return{
            "status":"relearning",
            "due":today,
            "interval":0,
            "ease":new_ease,
            "lapses":card.lapses+1,
            "reps":card.reps+1,
        }
    
    def __schedule_relearning_card(self,card:Card,rating:str,today:date) -> dict:
        # relearning + good  -> enter review, reset interval
        # relearning + again -> stay relearning, count one lapse
        if rating=="good":
            return {
                "status":"review",
                "due":today+timedelta(days=1),
                "interval":1,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
        elif rating=="again":
            return {
                "status":"relearning",
                "due":today,
                "interval":0,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
            }
    
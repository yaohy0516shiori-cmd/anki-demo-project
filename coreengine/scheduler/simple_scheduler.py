from datetime import datetime, timedelta, timezone, date
from card.cardmodel import Card

class Scheduler_v1:
    """
    Scheduler with same-day steps.

    State meaning:
    - new: never answered before
    - learning: same-day learning flow
    - review: graduated review flow
    - relearning: failed review, same-day recovery flow

    step_index meaning:
    - None for new/review
    - int >= 0 for learning/relearning

    Default rule in this file:
    - new -> learning(step_index=0) on first answer
    - learning needs 4 successful goods to graduate to review
    - review + again -> relearning(step_index=0)
    - relearning needs 3 successful goods to return to review

    It does NOT save anything.
    It only returns the calculated result.
    """
    valid_ratings=["good","again"]
    learning_steps=4
    relearning_steps=3

    def __init__(self):
        pass
    # Core scheduling algorithm. It only computes the next state and does not save
    # Unified scheduling entry, dispatch by card.status
    def schedule(self,card:Card,rating:str,today:date | None=None) -> dict:
        if rating not in self.valid_ratings:
            raise ValueError(f"Invalid rating: {rating}")
        
        today=today if today is not None else datetime.now(timezone.utc).date()

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
    
    # Compute next state for a new card
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
                "step_index":0,
            }
        elif rating=="again":
            return {
                "status":"new",
                "due":today, # why today?
                "interval":0,
                "ease":card.ease,
                "lapses":card.lapses,
                "reps":card.reps+1,
                "step_index":None, # 重复第一次展示（比如我后面每张复习卡可以设计不同的出卡方式？）
            }
    
    # Compute next state for a learning card
    def __schedule_learning_card(self,card:Card,rating:str,today:date) -> dict:
        # learning + good  -> enter review
        # learning + again -> stay learning
        if rating == "again":
            return {
                "status": "learning",
                "due": today,
                "interval": 0,
                "ease": card.ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": 0,
            }

        current_step = card.step_index if card.step_index is not None else 0
        next_step = current_step + 1

        if next_step >= self.learning_steps:
            return {
                "status": "review",
                "due": today + timedelta(days=1),
                "interval": 1,
                "ease": card.ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": None,
            }

        return {
            "status": "learning",
            "due": today,
            "interval": 0,
            "ease": card.ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": next_step,
        }

    # Compute next state for a review card
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
                "step_index":None,
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
            "step_index":0,
        }
    
    # Compute next state for a relearning card
    def __schedule_relearning_card(self,card:Card,rating:str,today:date) -> dict:
        # relearning + good  -> enter review, reset interval
        # relearning + again -> stay relearning, count one lapse
        if rating == "again":
            return {
                "status": "relearning",
                "due": today,
                "interval": 0,
                "ease": card.ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": 0,
            }

        current_step = card.step_index if card.step_index is not None else 0
        next_step = current_step + 1
        
        if next_step >= self.relearning_steps: # schedule里也没有循环啊？在哪里循环？
            return {
                "status": "review",
                "due": today + timedelta(days=1),
                "interval": 1,
                "ease": card.ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": None,
            }

        return {
            "status": "relearning",
            "due": today,
            "interval": 0,
            "ease": card.ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": next_step,
        }
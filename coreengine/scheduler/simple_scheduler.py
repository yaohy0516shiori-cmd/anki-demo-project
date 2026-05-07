from datetime import datetime, timedelta, timezone, date
from ..card.cardmodel import Card

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

    def __init__(self,learning_steps: int = 1, relearning_steps: int = 1):
        if learning_steps < 1:
            raise ValueError("learning_steps must be at least 1")
        if relearning_steps < 1:
            raise ValueError("relearning_steps must be at least 1")
        self.learning_steps = learning_steps
        self.relearning_steps = relearning_steps
        self.valid_rating = ['good', 'again']
        self.hint_good_ease_penalty = 0.05
        self.again_ease_penalty = 0.2

    def __apply_again_penalty(self, card: Card) -> dict:
        return {
            "ease": max(1.3, round(card.ease - self.again_ease_penalty, 2)),
            "lapses": card.lapses + 1,
            "reps": card.reps + 1,
        }

    def __apply_hint_good_ease(self, card: Card, used_hint: bool) -> float:
        if not used_hint:
            return card.ease
        return max(1.3, round(card.ease - self.hint_good_ease_penalty, 2))
    # Core scheduling algorithm. It only computes the next state and does not save
    # Unified scheduling entry, dispatch by card.status
    def schedule(self,card:Card,rating:str,today:date | None=None,review_context:dict|None=None) -> dict:
        review_context = review_context or {}
        use_hint = bool(review_context.get("hint_used"))
        if rating not in self.valid_ratings:
            raise ValueError(f"Invalid rating: {rating}")
        
        today=today if today is not None else datetime.now(timezone.utc).date()

        if card.status=="new":
            return self.__schedule_new_card(card,rating,today,use_hint)
        elif card.status=="learning":
            return self.__schedule_learning_card(card,rating,today,use_hint)
        elif card.status=="review":
            return self.__schedule_review_card(card,rating,today,use_hint)
        elif card.status=="relearning":
            return self.__schedule_relearning_card(card,rating,today,use_hint)
        else:
            raise ValueError(f"Invalid card status: {card.status}")
    
    # Compute next state for a new card
    def __schedule_new_card(self, card: Card, rating: str, today: date, used_hint: bool) -> dict:
        if rating == "again":
            penalty = self.__apply_again_penalty(card)
            return {
                "status": "learning",
                "due": today,
                "interval": 0,
                "ease": penalty["ease"],
                "lapses": penalty["lapses"],
                "reps": penalty["reps"],
                "step_index": 0,
            }

        new_ease = self.__apply_hint_good_ease(card, used_hint)

        return {
            "status": "learning",
            "due": today,
            "interval": 0,
            "ease": new_ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": 0,
        }
    
    # Compute next state for a learning card
    def __schedule_learning_card(self, card: Card, rating: str, today: date, used_hint: bool) -> dict:
        if rating == "again":
            penalty = self.__apply_again_penalty(card)
            return {
                "status": "learning",
                "due": today,
                "interval": 0,
                "ease": penalty["ease"],
                "lapses": penalty["lapses"],
                "reps": penalty["reps"],
                "step_index": 0,
            }

        new_ease = self.__apply_hint_good_ease(card, used_hint)

        current_step = card.step_index if card.step_index is not None else 0
        next_step = current_step + 1

        if next_step >= self.learning_steps:
            return {
                "status": "review",
                "due": today + timedelta(days=1),
                "interval": 1,
                "ease": new_ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": None,
            }

        return {
            "status": "learning",
            "due": today,
            "interval": 0,
            "ease": new_ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": next_step,
        }

    # Compute next state for a review card
    def __schedule_review_card(self, card: Card, rating: str, today: date, used_hint: bool) -> dict:
        if rating == "again":
            penalty = self.__apply_again_penalty(card)
            return {
                "status": "relearning",
                "due": today,
                "interval": 0,
                "ease": penalty["ease"],
                "lapses": penalty["lapses"],
                "reps": penalty["reps"],
                "step_index": 0,
            }

        new_ease = self.__apply_hint_good_ease(card, used_hint)
        base_interval = card.interval if card.interval > 0 else 1
        new_interval = max(round(base_interval * new_ease), base_interval + 1)

        return {
            "status": "review",
            "due": today + timedelta(days=new_interval),
            "interval": new_interval,
            "ease": new_ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": None,
        }

    # Compute next state for a relearning card
    def __schedule_relearning_card(self, card: Card, rating: str, today: date, used_hint: bool) -> dict:
        if rating == "again":
            penalty = self.__apply_again_penalty(card)
            return {
                "status": "relearning",
                "due": today,
                "interval": 0,
                "ease": penalty["ease"],
                "lapses": penalty["lapses"],
                "reps": penalty["reps"],
                "step_index": 0,
            }

        new_ease = self.__apply_hint_good_ease(card, used_hint)

        current_step = card.step_index if card.step_index is not None else 0
        next_step = current_step + 1

        if next_step >= self.relearning_steps:
            return {
                "status": "review",
                "due": today + timedelta(days=1),
                "interval": 1,
                "ease": new_ease,
                "lapses": card.lapses,
                "reps": card.reps + 1,
                "step_index": None,
            }

        return {
            "status": "relearning",
            "due": today,
            "interval": 0,
            "ease": new_ease,
            "lapses": card.lapses,
            "reps": card.reps + 1,
            "step_index": next_step,
        }

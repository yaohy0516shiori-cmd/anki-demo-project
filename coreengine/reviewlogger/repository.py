from .review import ReviewLog
from typing import List
from datetime import datetime
from .log_repository import ReviewLogRepository
# store review logs in memory
class InMemoryReviewLogRepository(ReviewLogRepository):
    def __init__(self):
        self.__logs={}
        self.__next_id=1
    
    # Serialize a review log to a dictionary
    def __seralize_log(self, log: ReviewLog) -> dict:
        return {
            "review_log_id": log.review_log_id,
            "user_id": log.user_id,
            "card_id": log.card_id,
            "deck_id": log.deck_id,
            "rating": log.rating,
            "old_status": log.old_status,
            "new_status": log.new_status,
            "old_due": log.old_due,
            "new_due": log.new_due,
            "old_interval": log.old_interval,
            "new_interval": log.new_interval,
            "old_ease": log.old_ease,
            "new_ease": log.new_ease,
            "old_lapses": log.old_lapses,
            "new_lapses": log.new_lapses,
            "old_reps": log.old_reps,
            "new_reps": log.new_reps,
            "old_step_index": log.old_step_index,
            "new_step_index": log.new_step_index,
            "hint_used": log.hint_used,
            "review_time": log.review_time,
        }

    # Deserialize a review log from a dictionary
    def __deserialize_log(self, data: dict) -> ReviewLog:
        return ReviewLog(
            review_log_id=data["review_log_id"],
            user_id=data["user_id"],
            card_id=data["card_id"],
            deck_id=data["deck_id"],
            rating=data["rating"],
            old_status=data["old_status"],
            new_status=data["new_status"],
            old_due=data["old_due"],
            new_due=data["new_due"],
            old_interval=data["old_interval"],
            new_interval=data["new_interval"],
            old_ease=data["old_ease"],
            new_ease=data["new_ease"],
            old_lapses=data["old_lapses"],
            new_lapses=data["new_lapses"],
            old_reps=data["old_reps"],
            new_reps=data["new_reps"],
            old_step_index=data["old_step_index"],
            new_step_index=data["new_step_index"],
            hint_used=data["hint_used"],
            review_time=data["review_time"],
        )
    
    # Add a review log
    def add_log(self, user_id:int, log: ReviewLog):
        if log.review_log_id is not None:
            raise ValueError("New Log ID must be None")
        if user_id not in self.__logs:
            self.__logs[user_id]={}
            log.review_log_id=1
        elif self.__logs[user_id][log.review_log_id] is not None:
            log.review_log_id+=1
        self.__next_id=log.review_log_id+1
        self.__logs[user_id][log.review_log_id]=self.__seralize_log(log)
        return self.__deserialize_log(self.__logs[user_id][log.review_log_id])

    # Get a review log by id
    def get_log(self, user_id:int, review_log_id: int) -> ReviewLog:
        data=self.__logs.get(user_id, {}).get(review_log_id)
        if not data:
            raise ValueError("Log not found")
        return self.__deserialize_log(data)
    
    # Update a review log
    def update_log(self, user_id:int, log: ReviewLog):
        if log.review_log_id is None:
            raise ValueError("Log ID must be set")
        self.__logs[user_id][log.review_log_id]=self.__seralize_log(log)
        return self.__deserialize_log(self.__logs[user_id][log.review_log_id])
    
    # Delete a review log
    def delete_log(self, user_id:int, review_log_id: int):
        raise NotImplementedError("V1 does not support deleting review logs")

    # Get all review logs by card id
    def get_logs_by_card_id(self, user_id:int, card_id: int) -> List[ReviewLog]:
        result=[]
        for data in self.__logs[user_id].values():
            if data["card_id"]==card_id:
                result.append(self.__deserialize_log(data))
        return result
    
    # Get all review logs
    def get_all_logs_by_user_id(self, user_id:int) -> List[ReviewLog]:
        return [self.__deserialize_log(data) for data in self.__logs[user_id].values()]

    # Count the number of review logs
    def count_logs_by_user_id(self, user_id:int) -> int:
        return len(self.__logs[user_id])
    
    # Get all review logs
    def get_all_logs(self) -> List[ReviewLog]:
        result=[]
        for user_id in self.__logs.keys():
            result.extend(self.get_all_logs_by_user_id(user_id))
        return result
    
    # Count the number of review logs
    def count_logs(self) -> int:
        return len(self.__logs)
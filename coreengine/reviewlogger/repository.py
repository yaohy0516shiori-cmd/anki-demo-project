from .review import ReviewLog
from typing import List
from datetime import datetime

# store review logs in memory
class ReviewLoggerRepository:
    def __init__(self):
        self.__logs={}
        self.__next_id=1
    
    # Serialize a review log to a dictionary
    def __seralize_log(self, log: ReviewLog) -> dict:
        return {
            "review_log_id": log.review_log_id,
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
            "review_time": log.review_time,
        }

    # Deserialize a review log from a dictionary
    def __deserialize_log(self, data: dict) -> ReviewLog:
        return ReviewLog(
            review_log_id=data["review_log_id"],
            card_id=data["card_id"],
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
            review_time=datetime(data["review_time"]),
        )
    
    # Add a review log
    def add_log(self, log: ReviewLog):
        if log.review_log_id is not None:
            raise ValueError("New Log ID must be None")
        log.review_log_id=self.__next_id  # 都不允许输入了为什么不直接在reviewlog里定死log_id=None? 其余同理 比如note_id
        self.__next_id+=1
        self.__logs[log.review_log_id]=self.__seralize_log(log)

        return self.__deserialize_log(self.__logs[log.review_log_id])

    # Get a review log by id
    def get_log(self, review_log_id: int) -> ReviewLog:
        data=self.__logs.get(review_log_id)
        if not data:
            raise ValueError("Log not found")
        return self.__deserialize_log(data)
    
    # Update a review log
    def update_log(self, log: ReviewLog):
        if log.review_log_id is None:
            raise ValueError("Log ID must be set")
        self.__logs[log.review_log_id]=self.__seralize_log(log)
        return self.__deserialize_log(self.__logs[log.review_log_id])
    
    # Delete a review log
    def delete_log(self, review_log_id: int):
        pass # 日志能删除吗？

    # Get all review logs by card id
    def get_log_by_card_id(self, card_id: int) -> List[ReviewLog]:
        result=[]
        for data in self.__logs.values():
            if data["card_id"]==card_id:
                result.append(self.__deserialize_log(data))
        return result
    
    # Get all review logs
    def get_all_logs(self) -> List[ReviewLog]:
        return [self.__deserialize_log(data) for data in self.__logs.values()]

    # Count the number of review logs
    def count_logs(self) -> int:
        return len(self.__logs)
    
    
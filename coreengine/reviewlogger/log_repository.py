from abc import ABC, abstractmethod

from .review import ReviewLog
from typing import List

class ReviewLogRepository(ABC):
    @abstractmethod
    def add_log(self, user_id:int, log: ReviewLog) -> ReviewLog:
        pass

    @abstractmethod
    def get_log(self, user_id:int, review_log_id: int) -> ReviewLog:
        pass

    @abstractmethod
    def update_log(self, user_id:int, log: ReviewLog) -> ReviewLog:
        pass

    @abstractmethod
    def delete_log(self, user_id:int, review_log_id: int) -> None:
        pass

    @abstractmethod
    def get_logs_by_card_id(self, user_id:int, card_id: int) -> List[ReviewLog]:
        pass

    @abstractmethod
    def get_all_logs_by_user_id(self, user_id:int) -> List[ReviewLog]:
        pass

    @abstractmethod
    def count_logs_by_user_id(self, user_id:int) -> int:
        pass

    @abstractmethod
    def get_all_logs(self) -> List[ReviewLog]:
        pass
    
    @abstractmethod
    def count_logs(self) -> int:
        pass

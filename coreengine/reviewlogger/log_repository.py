from abc import ABC, abstractmethod

from .review import ReviewLog


class ReviewLogRepository(ABC):
    @abstractmethod
    def add_log(self, log: ReviewLog) -> ReviewLog:
        pass

    @abstractmethod
    def get_log(self, review_log_id: int) -> ReviewLog:
        pass

    @abstractmethod
    def update_log(self, log: ReviewLog) -> ReviewLog:
        pass

    @abstractmethod
    def delete_log(self, review_log_id: int) -> None:
        pass

    @abstractmethod
    def get_logs_by_card_id(self, user_id:int, card_id: int) -> list[ReviewLog]:
        pass

    @abstractmethod
    def get_all_logs_by_user_id(self, user_id:int) -> list[ReviewLog]:
        pass

    @abstractmethod
    def count_logs_by_user_id(self, user_id:int) -> int:
        pass

    @abstractmethod
    def get_all_logs(self) -> list[ReviewLog]:
        pass
    
    @abstractmethod
    def count_logs(self) -> int:
        pass

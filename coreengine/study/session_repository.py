from abc import ABC, abstractmethod
from ..study.session import Session

class SessionRepository(ABC):
    @abstractmethod
    def create_session(self, session: Session) -> Session:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Session:
        pass

    @abstractmethod
    def update_session(self, session: Session) -> Session:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        pass
from .session_repository import SessionRepository
from .session import Session

class InMemoryStudySessionRepository(SessionRepository):
    def __init__(self):
        self.__sessions: dict[str, Session] = {}

    def create_session(self, session: Session) -> Session:
        self.__sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self.__sessions.get(session_id)

    def update_session(self, session: Session) -> Session:
        if session.session_id not in self.__sessions:
            raise ValueError("Session not found")
        session.touch()
        self.__sessions[session.session_id] = session
        return session

    def delete_session(self, session_id: str) -> None:
        self.__sessions.pop(session_id, None)
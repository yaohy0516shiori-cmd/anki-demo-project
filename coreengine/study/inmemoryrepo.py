from .session_repository import SessionRepository
from .session import Session

class InMemoryStudySessionRepository(SessionRepository):
    def __init__(self):
        self.__sessions: dict[str, Session] = {}

    def create_session(self, user_id:int, session: Session) -> Session:
        if user_id not in self.__sessions:
            self.__sessions[user_id] = {}
        self.__sessions[user_id][session.session_id] = session
        return session

    def get_session(self, user_id:int, session_id: str) -> Session | None:
        return self.__sessions.get(user_id, {}).get(session_id)

    def update_session(self, user_id:int, session: Session) -> Session:
        if session.session_id not in self.__sessions.get(user_id, {}):
            raise ValueError("Session not found")
        session.touch()
        self.__sessions[user_id][session.session_id] = session
        return session

    def delete_session(self, user_id:int, session_id: str) -> None:
        self.__sessions.get(user_id, {}).pop(session_id, None)
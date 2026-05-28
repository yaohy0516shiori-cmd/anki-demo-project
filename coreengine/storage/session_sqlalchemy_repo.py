from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from coreengine.study.session import Session
from coreengine.study.session_repository import SessionRepository
from coreengine.storage.sqlalchemy_models import StudySessionORM


class SqlAlchemyStudySessionRepository(SessionRepository):
    def __init__(self, db: DbSession):
        self.__db = db

    def __to_domain(self, orm: StudySessionORM) -> Session:
        return Session(
            session_id=orm.session_id,
            user_id=orm.user_id,
            deck_id=orm.deck_id,
            today=orm.today,
            status=orm.status,
            learning_queue=list(orm.learning_queue or []),
            review_queue=list(orm.review_queue or []),
            new_queue=list(orm.new_queue or []),
            current_card_id=orm.current_card_id,
            current_hint_used=bool(orm.current_hint_used),
            current_back_revealed=bool(orm.current_back_revealed),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def create_session(self, user_id: int, session: Session) -> Session:
        if session.user_id != user_id:
            raise ValueError("User ID does not match")

        orm = StudySessionORM(
            session_id=session.session_id,
            user_id=session.user_id,
            deck_id=session.deck_id,
            today=session.today,
            status=session.status,
            learning_queue=session.learning_queue,
            review_queue=session.review_queue,
            new_queue=session.new_queue,
            current_card_id=session.current_card_id,
            current_hint_used=session.current_hint_used,
            current_back_revealed=session.current_back_revealed,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

        self.__db.add(orm)
        self.__db.flush()
        return self.get_session(user_id, session.session_id)

    def get_session(self, user_id: int, session_id: str) -> Session:
        stmt = select(StudySessionORM).where(
            StudySessionORM.user_id == user_id,
            StudySessionORM.session_id == session_id,
        )

        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Session not found")

        return self.__to_domain(orm)

    def update_session(self, user_id: int, session: Session) -> Session:
        stmt = select(StudySessionORM).where(
            StudySessionORM.user_id == user_id,
            StudySessionORM.session_id == session.session_id,
        )

        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Session not found")

        orm.deck_id = session.deck_id
        orm.today = session.today
        orm.status = session.status
        orm.learning_queue = session.learning_queue
        orm.review_queue = session.review_queue
        orm.new_queue = session.new_queue
        orm.current_card_id = session.current_card_id
        orm.current_hint_used = session.current_hint_used
        orm.current_back_revealed = session.current_back_revealed
        orm.updated_at = session.updated_at

        self.__db.flush()
        return self.get_session(user_id, session.session_id)

    def delete_session(self, user_id: int, session_id: str) -> None:
        stmt = select(StudySessionORM).where(
            StudySessionORM.user_id == user_id,
            StudySessionORM.session_id == session_id,
        )

        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Session not found")

        self.__db.delete(orm)
        self.__db.flush()
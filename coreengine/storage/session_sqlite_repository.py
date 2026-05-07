import sqlite3
from ..study.session import Session
from ..study.session_repository import SessionRepository
from datetime import date, datetime
import json

class SqliteStudySessionRepository(SessionRepository):
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_session(self, session: Session) -> dict:
        return {
            "session_id": session.session_id,
            "deck_id": session.deck_id,
            "today": session.today.isoformat() if isinstance(session.today, date) else session.today,
            "status": session.status,
            "learning_queue": json.dumps(session.learning_queue, ensure_ascii=False),
            "review_queue": json.dumps(session.review_queue, ensure_ascii=False),
            "new_queue": json.dumps(session.new_queue, ensure_ascii=False),
            "current_card_id": session.current_card_id,
            "current_hint_used": 1 if session.current_hint_used else 0,
            "current_back_revealed": 1 if session.current_back_revealed else 0,
            "created_at": session.created_at.isoformat()
            if isinstance(session.created_at, datetime)
            else session.created_at,
            "updated_at": session.updated_at.isoformat()
            if isinstance(session.updated_at, datetime)
            else session.updated_at,
        }

    def __deserialize_session(self, row: sqlite3.Row) -> Session:
        return Session(
            session_id=row["session_id"],
            deck_id=row["deck_id"],
            today=date.fromisoformat(row["today"]),
            status=row["status"],
            learning_queue=json.loads(row["learning_queue"] or "[]"),
            review_queue=json.loads(row["review_queue"] or "[]"),
            new_queue=json.loads(row["new_queue"] or "[]"),
            current_card_id=row["current_card_id"],
            current_hint_used=bool(row["current_hint_used"]),
            current_back_revealed=bool(row["current_back_revealed"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_session(self, session: Session) -> Session:
        data=self.__serialize_session(session)
        cursor=self.__conn.execute("""
        INSERT INTO study_session (
            deck_id,
            today,
            status,
            learning_queue,
            review_queue,
            new_queue,
            current_card_id,
            current_hint_used,
            current_back_revealed,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data['deck_id'],
            data['today'],
            data['status'],
            data['learning_queue'],
            data['review_queue'],
            data['new_queue'],
            data['current_card_id'],
            data['current_hint_used'],
            data['current_back_revealed'],
            data['created_at'],
            data['updated_at']
        ))
        self.__conn.commit()
        return self.get_session(cursor.lastrowid)
    
    def get_session(self, session_id: int) -> Session:
        row=self.__conn.execute("""
        SELECT * FROM study_session WHERE session_id=?
        """,(session_id,)).fetchone()
        if row is None:
            raise ValueError("Session not found")
        return self.__deserialize_session(row)
    
    def update_session(self, session: Session) -> Session:
        data=self.__serialize_session(session)
        cursor=self.__conn.execute("""
        UPDATE study_session SET
        deck_id=?,
        today=?,
        status=?,
        learning_queue=?,
        review_queue=?,
        new_queue=?,
        current_card_id=?,
        current_hint_used=?,
        current_back_revealed=?,
        updated_at=?
        WHERE session_id=?
        """,(data['deck_id'], data['today'], data['status'], data['learning_queue'], data['review_queue'], data['new_queue'], data['current_card_id'], data['current_hint_used'], data['current_back_revealed'], data['updated_at'], session.session_id))
        if cursor.rowcount==0:
            raise ValueError("Session not found")
        self.__conn.commit()
        return self.get_session(session.session_id)
    
    def delete_session(self, session_id: int) -> None:
        cursor=self.__conn.execute("""
        DELETE FROM study_session WHERE session_id=?
        """,(session_id,))
        if cursor.rowcount==0:
            raise ValueError("Session not found")
        self.__conn.commit()
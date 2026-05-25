from pathlib import Path
from typing import Generator
import sqlite3
from backend.app.auth import decode_access_token
from fastapi import Depends, Header, HTTPException
from backend.app.email_code_service import InMemoryEmailCodeService
from coreengine.storage.sqlite_connection import (
    create_connection,
    close_connection,
    SqliteTransactionManager,
)
from coreengine.storage.schema import init_db

from coreengine.storage.user_sqlite_repository import SqliteUserRepository
from coreengine.storage.note_sqlite_repository import SqliteNoteRepository
from coreengine.storage.card_sqlite_repository import SqliteCardRepository
from coreengine.storage.deck_sqlite_repository import SqliteDeckRepository
from coreengine.storage.reviewlog_sqlite_repository import SqliteReviewLogRepository
from coreengine.storage.session_sqlite_repository import SqliteStudySessionRepository

from coreengine.user.service import UserService
from coreengine.note.service import NoteService
from coreengine.card.service import CardService
from coreengine.deck.service import DeckService
from coreengine.reviewlogger.service import ReviewLoggerService
from coreengine.scheduler.simple_scheduler import Scheduler_v1
from coreengine.study.service import StudyService

'''
CREATE DEPENDENCIES HERE: REPO, SERVICE, UTILITIES, ETC.
get_conn: get a connection to the database
get_transaction_manager: get a transaction manager
get_note_repo: get a note repository
get_card_repo: get a card repository
get_deck_repo: get a deck repository
get_review_repo: get a review repository
get_card_service: get a card service
get_note_service: get a note service
get_deck_service: get a deck service
get_review_service: get a review service
get_study_service: get a study service
get_current_user_id()
    从 HTTP Header 读取当前用户 ID
get_conn()
    每个请求创建 SQLite connection，请求结束后关闭
get_*_repo()
    给 repository 注入同一个 conn
get_*_service()
    给 service 注入 repo 和 transaction manager
get_session_repo()
    修掉之前 SESSION_REPO 全局错误
'''

DB_PATH=Path(__file__).parent.parent.parent / "database" / "anki_demo.db"
_email_code_service = InMemoryEmailCodeService(ttl_minutes=5)

def get_email_code_service():
    return _email_code_service
    
def get_conn()->Generator[sqlite3.Connection,None,None]:
    conn=create_connection(str(DB_PATH))
    init_db(conn)
    try:
        yield conn
    finally:
        close_connection(conn)

def get_transaction_manager(conn=Depends(get_conn)):
    return SqliteTransactionManager(conn)

def get_user_repo(conn=Depends(get_conn)):
    return SqliteUserRepository(conn)

def get_note_repo(conn=Depends(get_conn)):
    return SqliteNoteRepository(conn)


def get_card_repo(conn=Depends(get_conn)):
    return SqliteCardRepository(conn)


def get_deck_repo(conn=Depends(get_conn)):
    return SqliteDeckRepository(conn)


def get_review_repo(conn=Depends(get_conn)):
    return SqliteReviewLogRepository(conn)

def get_session_repo(conn=Depends(get_conn)):
    return SqliteStudySessionRepository(conn)

def get_user_service(
    user_repo=Depends(get_user_repo),
    deck_repo=Depends(get_deck_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return UserService(user_repo, deck_repo, transaction_manager)

def get_card_service(
    card_repo=Depends(get_card_repo),
    note_repo=Depends(get_note_repo),
    deck_repo=Depends(get_deck_repo)
):
    return CardService(card_repo, note_repo, deck_repo)


def get_note_service(
    note_repo=Depends(get_note_repo),
    card_service=Depends(get_card_service),
    deck_repo=Depends(get_deck_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return NoteService(note_repo, card_service, deck_repo, transaction_manager)


def get_deck_service(
    deck_repo=Depends(get_deck_repo),
    card_service=Depends(get_card_service),
    transaction_manager=Depends(get_transaction_manager),
):
    return DeckService(deck_repo, card_service, transaction_manager)


def get_review_service(
    card_repo=Depends(get_card_repo),
    review_repo=Depends(get_review_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    scheduler = Scheduler_v1()
    return ReviewLoggerService(card_repo, review_repo, scheduler, transaction_manager)

def get_study_service(
    card_repo=Depends(get_card_repo),
    review_service=Depends(get_review_service),
    note_repo=Depends(get_note_repo),
    deck_repo=Depends(get_deck_repo),
    session_repo=Depends(get_session_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return StudyService(card_repo, review_service, note_repo, deck_repo, session_repo, transaction_manager)

def get_current_user_id(authorization: str = Header(..., alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.removeprefix("Bearer ").strip()
    return decode_access_token(token)
from pathlib import Path
from typing import Generator
from fastapi import FastAPI,Depends
from coreengine.storage.sqlite_connection import create_connection, close_connection
from coreengine.storage.schema import init_db
from coreengine.storage.note_sqlite_repository import SqliteNoteRepository
from coreengine.storage.card_sqlite_repository import SqliteCardRepository
from coreengine.storage.deck_sqlite_repository import SqliteDeckRepository
from coreengine.storage.reviewlog_sqlite_repository import SqliteReviewLogRepository
from coreengine.note.service import NoteService
from coreengine.card.service import CardService
from coreengine.reviewlogger.service import ReviewLoggerService
from coreengine.scheduler.simple_scheduler import Scheduler_v1
from coreengine.study.service import StudyService
import sqlite3
from coreengine.deck.service import DeckService
from coreengine.study.inmemoryrepo import InMemoryStudySessionRepository

DB_PATH=Path(__file__).parent.parent.parent / "database" / "anki_demo.db"

def get_conn()->Generator[sqlite3.Connection,None,None]:
    conn=create_connection(str(DB_PATH))
    init_db(conn)
    try:
        yield conn
    finally:
        close_connection(conn)

def get_note_repo(conn=Depends(get_conn)):
    return SqliteNoteRepository(conn)


def get_card_repo(conn=Depends(get_conn)):
    return SqliteCardRepository(conn)


def get_deck_repo(conn=Depends(get_conn)):
    return SqliteDeckRepository(conn)


def get_review_repo(conn=Depends(get_conn)):
    return SqliteReviewLogRepository(conn)


def get_card_service(
    card_repo=Depends(get_card_repo),
    note_repo=Depends(get_note_repo),
):
    return CardService(card_repo, note_repo)


def get_note_service(
    note_repo=Depends(get_note_repo),
    card_service=Depends(get_card_service),
):
    return NoteService(note_repo, card_service)


def get_deck_service(
    deck_repo=Depends(get_deck_repo),
    card_service=Depends(get_card_service),
):
    return DeckService(deck_repo, card_service)


def get_review_service(
    card_repo=Depends(get_card_repo),
    review_repo=Depends(get_review_repo),
):
    scheduler = Scheduler_v1()
    return ReviewLoggerService(card_repo, review_repo, scheduler)



SESSION_REPO = InMemoryStudySessionRepository()

def get_session_repo():
    return SESSION_REPO

def get_study_service(
    card_repo=Depends(get_card_repo),
    review_service=Depends(get_review_service),
    note_repo=Depends(get_note_repo),
    deck_repo=Depends(get_deck_repo),
    session_repo=Depends(get_session_repo),
):
    return StudyService(card_repo, review_service, note_repo, deck_repo, session_repo)
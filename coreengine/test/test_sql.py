from datetime import date
from pathlib import Path

from ..storage.sqlite_connection import create_connection, close_connection
from ..storage.schema import init_db
from ..storage.note_sqlite_repository import SqliteNoteRepository
from ..storage.card_sqlite_repository import SqliteCardRepository
from ..storage.reviewlog_sqlite_repository import SqliteReviewLogRepository

from ..note.service import NoteService
from ..note_type.type_registry import BASIC
from ..card.service import CardService
from ..reviewlogger.service import ReviewLoggerService
from ..scheduler.simple_scheduler import Scheduler_v1
from ..study.service import StudyService


TODAY = date(2026, 4, 3)


def build_sqlite_app(db_path="data/test_anki_demo.db"):
    conn = create_connection(db_path)
    init_db(conn)

    note_repo = SqliteNoteRepository(conn)
    card_repo = SqliteCardRepository(conn)
    review_repo = SqliteReviewLogRepository(conn)

    card_service = CardService(card_repo)
    note_service = NoteService(note_repo, card_service)
    scheduler = Scheduler_v1()
    review_service = ReviewLoggerService(card_repo, review_repo, scheduler)
    study_service = StudyService(card_repo, review_service, note_repo)

    return {
        "conn": conn,
        "note_repo": note_repo,
        "card_repo": card_repo,
        "review_repo": review_repo,
        "card_service": card_service,
        "note_service": note_service,
        "review_service": review_service,
        "scheduler": scheduler,
        "study_service": study_service,
    }


def test_sqlite_create_note_and_review_once():
    app = build_sqlite_app()

    try:
        note_id = app["note_service"].create_note(BASIC, ["hello", "你好"], [], today=TODAY)

        cards = app["card_service"].get_card_by_note_id(note_id)
        assert len(cards) == 1

        study_service = app["study_service"]
        study_service.start_study_session(today=TODAY)

        item = study_service.get_next_card()
        assert item is not None
        assert item["front"] == "hello"

        back = study_service.reveal_back_of_current_card()
        assert back == "你好"

        result = study_service.rate_current_card("good")
        updated_card = result["card"]
        log = result["log"]

        assert updated_card.status == "learning"
        assert updated_card.step_index == 0
        assert log.old_status == "new"
        assert log.new_status == "learning"
        assert app["review_repo"].count_logs() == 1

    finally:
        close_connection(app["conn"])
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


def build_sqlite_app(db_path="database/test_anki_demo.db"):
    db_path = Path(db_path)
    print(f"DB path: {db_path.resolve()}")

    conn = create_connection(db_path)
    init_db(conn)

    print(f"DB exists after init: {db_path.exists()}")

    tables = conn.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """).fetchall()
    print("Tables:", [row["name"] for row in tables])

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


if __name__ == "__main__":
    app = build_sqlite_app()
    try:
        note_id = app["note_service"].create_note(BASIC, ["hello", "你好"], [], today=TODAY)
        print(f"Created note_id={note_id}")

        cards = app["card_service"].get_card_by_note_id(note_id)
        print(f"Card count: {len(cards)}")
    finally:
        close_connection(app["conn"])
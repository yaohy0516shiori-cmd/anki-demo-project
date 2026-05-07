import pytest
from datetime import date, timedelta

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

from coreengine.note_type.type_registry import BASIC, BASIC_REVERSE, CLOZE


@pytest.fixture
def app_ctx(tmp_path):
    db_path = tmp_path / "anki_test.db"
    conn = create_connection(str(db_path))
    init_db(conn)

    note_repo = SqliteNoteRepository(conn)
    card_repo = SqliteCardRepository(conn)
    deck_repo = SqliteDeckRepository(conn)
    review_repo = SqliteReviewLogRepository(conn)

    card_service = CardService(card_repo, note_repo)
    note_service = NoteService(note_repo, card_service)

    # 用 1/1 是为了让测试更短
    scheduler = Scheduler_v1(learning_steps=1, relearning_steps=1)
    review_service = ReviewLoggerService(card_repo, review_repo, scheduler)
    study_service = StudyService(card_repo, review_service, note_repo, deck_repo)

    ctx = {
        "conn": conn,
        "note_repo": note_repo,
        "card_repo": card_repo,
        "deck_repo": deck_repo,
        "review_repo": review_repo,
        "card_service": card_service,
        "note_service": note_service,
        "review_service": review_service,
        "study_service": study_service,
    }

    yield ctx
    close_connection(conn)


def test_init_db_creates_default_deck(app_ctx):
    deck = app_ctx["deck_repo"].get_default_deck()
    assert deck.deck_id == 1
    assert deck.deck_name == "Default"


def test_basic_note_generates_one_card(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        BASIC,
        ["front-basic", "back-basic"],
        tags=["tag1"],
        hint="hint-basic",
        today=today,
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(cards) == 1
    assert cards[0].template_ord == 0
    assert cards[0].status == "new"
    assert cards[0].deck_id == 1
    assert cards[0].due == today


def test_basic_reverse_generates_two_cards(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        BASIC_REVERSE,
        ["front-r", "back-r"],
        today=today,
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(cards) == 2
    assert [c.template_ord for c in cards] == [0, 1]


def test_cloze_generates_multiple_cards(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        CLOZE,
        ["I like {{c1::cats}} and {{c2::dogs::animal}}", "extra info"],
        today=today,
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(cards) == 2
    assert [c.template_ord for c in cards] == [0, 1]


def test_cloze_update_reconciles_cards(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        CLOZE,
        ["I like {{c1::cats}} and {{c2::dogs}}", "extra info"],
        today=today,
    )

    cards_before = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert len(cards_before) == 2

    app_ctx["note_service"].update_note(
        note_id,
        fields=["I like {{c1::cats}}", "extra info"],
        today=today,
    )

    cards_after = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert len(cards_after) == 1
    assert cards_after[0].template_ord == 0


def test_study_session_flow_and_review_log(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        BASIC,
        ["front-study", "back-study"],
        hint="hint-study",
        today=today,
    )

    session_info = app_ctx["study_service"].start_study_session(deck_id=1, today=today)
    assert session_info["deck_id"] == 1
    assert session_info["new_queue"] == 1

    next_card = app_ctx["study_service"].get_next_card()
    assert next_card["front"] == "front-study"
    assert next_card["status"] == "new"
    assert next_card["hint_available"] is True

    hint = app_ctx["study_service"].reveal_hint_of_current_card()
    assert hint == "hint-study"

    back = app_ctx["study_service"].reveal_back_of_current_card()
    assert back == "back-study"

    # 第一次 good: new -> learning
    result_1 = app_ctx["study_service"].rate_current_card("good")
    card_1 = result_1["card"]
    log_1 = result_1["log"]

    assert card_1.status == "learning"
    assert card_1.step_index == 0
    assert card_1.due == today
    assert log_1.old_status == "new"
    assert log_1.new_status == "learning"
    assert log_1.hint_used is True

    # 第二次 good: learning -> review
    next_card_again = app_ctx["study_service"].get_next_card()
    assert next_card_again["front"] == "front-study"

    result_2 = app_ctx["study_service"].rate_current_card("good")
    card_2 = result_2["card"]
    log_2 = result_2["log"]

    assert card_2.status == "review"
    assert card_2.step_index is None
    assert card_2.interval == 1
    assert card_2.due == today + timedelta(days=1)
    assert log_2.old_status == "learning"
    assert log_2.new_status == "review"

    logs = app_ctx["review_repo"].get_logs_by_card_id(card_2.card_id)
    assert len(logs) == 2


def test_review_again_goes_to_relearning(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        BASIC,
        ["front-again", "back-again"],
        today=today,
    )

    app_ctx["study_service"].start_study_session(deck_id=1, today=today)

    # good -> learning
    app_ctx["study_service"].get_next_card()
    app_ctx["study_service"].rate_current_card("good")

    # good -> review
    app_ctx["study_service"].get_next_card()
    app_ctx["study_service"].rate_current_card("good")

    # 下一天复习，again -> relearning
    tomorrow = today + timedelta(days=1)
    app_ctx["study_service"].start_study_session(deck_id=1, today=tomorrow)

    app_ctx["study_service"].get_next_card()
    result = app_ctx["study_service"].rate_current_card("again")

    card = result["card"]
    log = result["log"]

    assert card.status == "relearning"
    assert card.step_index == 0
    assert card.due == tomorrow
    assert card.lapses == 1
    assert log.old_status == "review"
    assert log.new_status == "relearning"
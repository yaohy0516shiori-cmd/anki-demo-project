import pytest
from datetime import date, timedelta

from coreengine.storage.sqlite_connection import create_connection, close_connection
from coreengine.storage.schema import init_db

from coreengine.storage.note_sqlite_repository import SqliteNoteRepository
from coreengine.storage.card_sqlite_repository import SqliteCardRepository
from coreengine.storage.deck_sqlite_repository import SqliteDeckRepository
from coreengine.storage.reviewlog_sqlite_repository import SqliteReviewLogRepository

from coreengine.study.inmemoryrepo import InMemoryStudySessionRepository

from coreengine.note.service import NoteService
from coreengine.card.service import CardService
from coreengine.deck.service import DeckService
from coreengine.reviewlogger.service import ReviewLoggerService
from coreengine.study.service import StudyService

from coreengine.scheduler.simple_scheduler import Scheduler_v1
from coreengine.note_type.type_registry import BASIC, BASIC_REVERSE, CLOZE
from coreengine.deck.deckmodel import Deck


@pytest.fixture
def app_ctx(tmp_path):
    db_path = tmp_path / "anki_test.db"

    conn = create_connection(str(db_path))
    init_db(conn)

    note_repo = SqliteNoteRepository(conn)
    card_repo = SqliteCardRepository(conn)
    deck_repo = SqliteDeckRepository(conn)
    review_repo = SqliteReviewLogRepository(conn)
    session_repo = InMemoryStudySessionRepository()

    card_service = CardService(card_repo, note_repo)
    note_service = NoteService(note_repo, card_service)
    deck_service = DeckService(deck_repo, card_service)

    # learning_steps=1 / relearning_steps=1 是为了让测试流程更短：
    # 第一次 good: new -> learning
    # 第二次 good: learning -> review
    scheduler = Scheduler_v1(learning_steps=1, relearning_steps=1)
    review_service = ReviewLoggerService(card_repo, review_repo, scheduler)

    study_service = StudyService(
        card_repo=card_repo,
        review_service=review_service,
        note_repo=note_repo,
        deck_repo=deck_repo,
        session_repo=session_repo,
    )

    yield {
        "conn": conn,
        "note_repo": note_repo,
        "card_repo": card_repo,
        "deck_repo": deck_repo,
        "review_repo": review_repo,
        "session_repo": session_repo,
        "card_service": card_service,
        "note_service": note_service,
        "deck_service": deck_service,
        "review_service": review_service,
        "study_service": study_service,
    }

    close_connection(conn)


def test_backend_core_import_chain_can_be_constructed(app_ctx):
    assert app_ctx["note_service"] is not None
    assert app_ctx["card_service"] is not None
    assert app_ctx["deck_service"] is not None
    assert app_ctx["review_service"] is not None
    assert app_ctx["study_service"] is not None


def test_create_basic_note_generates_one_due_card(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["front-basic", "back-basic"],
        hint="hint-basic",
        today=today,
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(cards) == 1
    assert cards[0].note_id == note_id
    assert cards[0].deck_id == 1
    assert cards[0].template_ord == 0
    assert cards[0].status == "new"
    assert cards[0].due == today


def test_create_basic_reverse_generates_two_cards(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC_REVERSE,
        fields=["front", "back"],
        today=today,
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(cards) == 2
    assert [card.template_ord for card in cards] == [0, 1]


def test_update_cloze_note_reconciles_cards(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        note_type=CLOZE,
        fields=["I like {{c1::cats}} and {{c2::dogs}}", "extra"],
        today=today,
    )

    before = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert len(before) == 2

    app_ctx["note_service"].update_note(
        note_id=note_id,
        fields=["I like {{c1::cats}}", "extra"],
        today=today,
    )

    after = app_ctx["card_service"].get_cards_by_note_id(note_id)

    assert len(after) == 1
    assert after[0].template_ord == 0


def test_study_session_pop_rate_reenqueue_and_review_log(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["front-study", "back-study"],
        hint="hint-study",
        today=today,
    )

    session_info = app_ctx["study_service"].start_study_session(
        deck_id=1,
        today=today,
    )

    session_id = session_info["session_id"]

    assert session_info["deck_id"] == 1
    assert session_info["new_queue"] == 1
    assert session_info["learning_queue"] == 0
    assert session_info["review_queue"] == 0

    next_card = app_ctx["study_service"].get_next_card(session_id)

    assert next_card["front"] == "front-study"
    assert next_card["status"] == "new"
    assert next_card["hint_available"] is True
    assert next_card["note"]["fields"] == ["front-study", "back-study"]

    hint = app_ctx["study_service"].reveal_hint_of_current_card(session_id)
    assert hint == "hint-study"

    back = app_ctx["study_service"].reveal_back_of_current_card(session_id)
    assert back == "back-study"

    result_1 = app_ctx["study_service"].rate_current_card(session_id, "good")
    card_1 = result_1["card"]
    log_1 = result_1["log"]

    assert card_1.status == "learning"
    assert card_1.step_index == 0
    assert card_1.due == today
    assert log_1.old_status == "new"
    assert log_1.new_status == "learning"
    assert log_1.hint_used is True

    next_card_again = app_ctx["study_service"].get_next_card(session_id)
    assert next_card_again["front"] == "front-study"

    result_2 = app_ctx["study_service"].rate_current_card(session_id, "good")
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

    assert app_ctx["study_service"].is_finished(session_id) is True


def test_review_again_goes_to_relearning_next_day(app_ctx):
    today = date(2026, 4, 22)

    app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["front-again", "back-again"],
        today=today,
    )

    session_info = app_ctx["study_service"].start_study_session(
        deck_id=1,
        today=today,
    )
    session_id = session_info["session_id"]

    app_ctx["study_service"].get_next_card(session_id)
    app_ctx["study_service"].rate_current_card(session_id, "good")

    app_ctx["study_service"].get_next_card(session_id)
    app_ctx["study_service"].rate_current_card(session_id, "good")

    tomorrow = today + timedelta(days=1)

    tomorrow_session = app_ctx["study_service"].start_study_session(
        deck_id=1,
        today=tomorrow,
    )
    tomorrow_session_id = tomorrow_session["session_id"]

    app_ctx["study_service"].get_next_card(tomorrow_session_id)
    result = app_ctx["study_service"].rate_current_card(
        tomorrow_session_id,
        "again",
    )

    card = result["card"]
    log = result["log"]

    assert card.status == "relearning"
    assert card.step_index == 0
    assert card.due == tomorrow
    assert card.lapses == 1
    assert log.old_status == "review"
    assert log.new_status == "relearning"


def test_service_delete_note_returns_message_and_counts(app_ctx):
    today = date(2026, 4, 22)

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["delete-front", "delete-back"],
        today=today,
    )

    cards_before = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert len(cards_before) == 1

    result = app_ctx["note_service"].delete_note(note_id)

    assert result["note_id"] == note_id
    assert result["deleted_note_count"] == 1
    assert result["deleted_card_count"] == 1
    assert result["message"] == f"deleted 1 note and 1 cards for note {note_id}"

    with pytest.raises(ValueError):
        app_ctx["note_service"].get_note(note_id)

    assert app_ctx["card_service"].get_cards_by_note_id(note_id) == []


def test_safe_delete_deck_moves_cards_to_default_and_returns_message(app_ctx):
    today = date(2026, 4, 22)

    deck = app_ctx["deck_service"].create_deck(
        Deck(deck_name="Temporary Deck", deck_description="for delete test")
    )

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["deck-front", "deck-back"],
        deck_id=deck.deck_id,
        today=today,
    )

    cards_before = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert cards_before[0].deck_id == deck.deck_id

    result = app_ctx["deck_service"].delete_deck(deck.deck_id)

    assert result["deleted_deck_id"] == deck.deck_id
    assert result["deleted_deck_count"] == 1
    assert result["moved_card_count"] == 1
    assert result["target_deck_id"] == 1
    assert "deleted deck" in result["message"]

    cards_after = app_ctx["card_service"].get_cards_by_note_id(note_id)
    assert cards_after[0].deck_id == 1

    with pytest.raises(ValueError):
        app_ctx["deck_service"].get_deck(deck.deck_id)


def test_hard_delete_deck_deletes_cards_and_returns_message(app_ctx):
    today = date(2026, 4, 22)

    deck = app_ctx["deck_service"].create_deck(
        Deck(deck_name="Hard Delete Deck", deck_description="delete cards too")
    )

    note_id = app_ctx["note_service"].create_note(
        note_type=BASIC,
        fields=["hard-front", "hard-back"],
        deck_id=deck.deck_id,
        today=today,
    )

    assert len(app_ctx["card_service"].get_cards_by_note_id(note_id)) == 1

    result = app_ctx["deck_service"].delete_deck_and_cards(deck.deck_id)

    assert result["deleted_deck_id"] == deck.deck_id
    assert result["deleted_deck_count"] == 1
    assert result["deleted_card_count"] == 1
    assert "deleted deck" in result["message"]

    assert app_ctx["card_service"].get_cards_by_note_id(note_id) == []

    with pytest.raises(ValueError):
        app_ctx["deck_service"].get_deck(deck.deck_id)
# test core study flow: start session, get next card, rate card, end session

from datetime import date, timedelta

import pytest

from coreengine.note_type.type_registry import get_note_type


TODAY = date(2026, 1, 1)


def _create_user(core_services, prefix: str = "study") -> int:
    return core_services.user.register_user(
        email=f"{prefix}@example.com",
        username=prefix,
        password="Password123",
    )


def _get_default_deck(core_services, user_id: int):
    decks = core_services.deck.get_all_decks(user_id)
    default_decks = [deck for deck in decks if deck.is_default is True]

    assert len(default_decks) == 1

    return default_decks[0]


def _create_basic_note(core_services, user_id: int, today: date):
    return core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(1),
        fields=["Capital of France?", "Paris"],
        tags=["study"],
        hint="capital city",
        today=today,
    )


def test_start_study_session_puts_due_new_card_into_new_queue(core_services):
    user_id = _create_user(core_services, "study_due")
    default_deck = _get_default_deck(core_services, user_id)

    _create_basic_note(
        core_services=core_services,
        user_id=user_id,
        today=TODAY,
    )

    session = core_services.study.start_study_session(
        user_id=user_id,
        deck_id=default_deck.deck_id,
        today=TODAY,
    )

    assert session["user_id"] == user_id
    assert session["deck_id"] == default_deck.deck_id
    assert session["deck_name"] == "Default"
    assert session["learning_queue"] == 0
    assert session["review_queue"] == 0
    assert session["new_queue"] == 1
    assert isinstance(session["session_id"], str)
    assert session["session_id"]


def test_start_study_session_excludes_future_due_cards(core_services):
    user_id = _create_user(core_services, "study_future")
    default_deck = _get_default_deck(core_services, user_id)

    _create_basic_note(
        core_services=core_services,
        user_id=user_id,
        today=TODAY + timedelta(days=1),
    )

    session = core_services.study.start_study_session(
        user_id=user_id,
        deck_id=default_deck.deck_id,
        today=TODAY,
    )

    assert session["learning_queue"] == 0
    assert session["review_queue"] == 0
    assert session["new_queue"] == 0

    next_card = core_services.study.get_next_card(
        user_id=user_id,
        session_id=session["session_id"],
    )

    assert next_card is None

    assert core_services.study.is_finished(
        user_id=user_id,
        session_id=session["session_id"],
    ) is True


def test_study_next_hint_back_rate_flow(core_services):
    user_id = _create_user(core_services, "study_flow")
    default_deck = _get_default_deck(core_services, user_id)

    note_id = _create_basic_note(
        core_services=core_services,
        user_id=user_id,
        today=TODAY,
    )

    cards = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 1

    session = core_services.study.start_study_session(
        user_id=user_id,
        deck_id=default_deck.deck_id,
        today=TODAY,
    )

    session_id = session["session_id"]

    next_card = core_services.study.get_next_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert next_card["user_id"] == user_id
    assert next_card["session_id"] == session_id
    assert next_card["front"] == "Capital of France?"
    assert next_card["hint_available"] is True
    assert next_card["card"]["note_id"] == note_id
    assert next_card["card"]["status"] == "new"

    with pytest.raises(ValueError, match="Finish the current card"):
        core_services.study.get_next_card(
            user_id=user_id,
            session_id=session_id,
        )

    hint = core_services.study.reveal_hint_of_current_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert hint == "capital city"

    back = core_services.study.reveal_back_of_current_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert back == "Paris"

    first_rate_result = core_services.study.rate_current_card(
        user_id=user_id,
        session_id=session_id,
        rating="good",
    )

    first_card = first_rate_result["card"]
    first_log = first_rate_result["log"]

    assert first_card.reps == 1
    assert first_card.status == "learning"
    assert first_card.due == TODAY
    assert first_log.rating == "good"
    assert first_log.old_status == "new"
    assert first_log.new_status == "learning"
    assert first_log.hint_used is True

    assert core_services.study.is_finished(
        user_id=user_id,
        session_id=session_id,
    ) is False

    learning_card = core_services.study.get_next_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert learning_card["card"]["card_id"] == first_card.card_id
    assert learning_card["card"]["status"] == "learning"

    second_back = core_services.study.reveal_back_of_current_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert second_back == "Paris"

    second_rate_result = core_services.study.rate_current_card(
        user_id=user_id,
        session_id=session_id,
        rating="good",
    )

    second_card = second_rate_result["card"]
    second_log = second_rate_result["log"]

    assert second_card.reps == 2
    assert second_card.status == "review"
    assert second_card.due == TODAY + timedelta(days=1)
    assert second_card.interval == 1
    assert second_log.old_status == "learning"
    assert second_log.new_status == "review"

    assert core_services.study.is_finished(
        user_id=user_id,
        session_id=session_id,
    ) is True

    logs = core_services.review.get_all_review_logs_history(user_id)

    assert len(logs) == 2
    assert [log.rating for log in logs] == ["good", "good"]


def test_reveal_hint_after_back_is_rejected(core_services):
    user_id = _create_user(core_services, "study_hint_after_back")
    default_deck = _get_default_deck(core_services, user_id)

    _create_basic_note(
        core_services=core_services,
        user_id=user_id,
        today=TODAY,
    )

    session = core_services.study.start_study_session(
        user_id=user_id,
        deck_id=default_deck.deck_id,
        today=TODAY,
    )

    session_id = session["session_id"]

    core_services.study.get_next_card(
        user_id=user_id,
        session_id=session_id,
    )

    back = core_services.study.reveal_back_of_current_card(
        user_id=user_id,
        session_id=session_id,
    )

    assert back == "Paris"

    with pytest.raises(ValueError, match="Back of the current card"):
        core_services.study.reveal_hint_of_current_card(
            user_id=user_id,
            session_id=session_id,
        )


def test_user_cannot_access_other_users_study_session(core_services):
    user1_id = _create_user(core_services, "study_user1")
    user2_id = _create_user(core_services, "study_user2")

    user1_default_deck = _get_default_deck(core_services, user1_id)

    _create_basic_note(
        core_services=core_services,
        user_id=user1_id,
        today=TODAY,
    )

    session = core_services.study.start_study_session(
        user_id=user1_id,
        deck_id=user1_default_deck.deck_id,
        today=TODAY,
    )

    with pytest.raises(ValueError):
        core_services.study.get_next_card(
            user_id=user2_id,
            session_id=session["session_id"],
        )
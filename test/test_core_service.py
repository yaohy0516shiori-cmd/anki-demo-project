# test/test_core_services.py

import pytest

from coreengine.note_type.type_registry import get_note_type


def test_core_register_user_creates_default_deck(core_services):
    user_id = core_services.user.register_user(
        email="test@example.com",
        username="tester",
        password="Password123",
    )

    user = core_services.user.get_user(user_id)
    assert user.email == "test@example.com"

    decks = core_services.deck.get_all_decks(user_id)

    assert len(decks) == 1
    assert decks[0].is_default is True
    assert decks[0].deck_name == "Default"


def test_core_duplicate_email_is_rejected(core_services):
    core_services.user.register_user(
        email="test@example.com",
        username="tester1",
        password="Password123",
    )

    with pytest.raises(ValueError):
        core_services.user.register_user(
            email="test@example.com",
            username="tester2",
            password="Password123",
        )


def test_core_create_basic_note_generates_one_card(core_services):
    user_id = core_services.user.register_user(
        email="test@example.com",
        username="tester",
        password="Password123",
    )

    note_type = get_note_type(1)

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=note_type,
        fields=["Capital of France?", "Paris"],
        tags=["geo"],
        hint="capital city",
    )

    note = core_services.note.get_note(user_id, note_id)
    assert note.fields == ["Capital of France?", "Paris"]
    assert note.hint == "capital city"

    cards = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 1
    assert cards[0].user_id == user_id
    assert cards[0].note_id == note_id
    assert cards[0].status == "new"
# test core note card flow: create note, create cards, update note, update cards

# test/test_core_note_card_flow.py

from datetime import date

import pytest

from coreengine.deck.deckmodel import Deck
from coreengine.note_type.type_registry import get_note_type


TODAY = date(2026, 1, 1)


def _create_user(core_services, prefix: str = "user") -> int:
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


def test_create_basic_note_generates_one_card_in_default_deck(core_services):
    user_id = _create_user(core_services, "basic")
    default_deck = _get_default_deck(core_services, user_id)

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(1),
        fields=["Capital of France?", "Paris"],
        tags=["geo"],
        hint="capital city",
        today=TODAY,
    )

    note = core_services.note.get_note(user_id, note_id)
    cards = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert note.user_id == user_id
    assert note.fields == ["Capital of France?", "Paris"]
    assert note.tags == ["geo"]
    assert note.hint == "capital city"

    assert len(cards) == 1
    assert cards[0].user_id == user_id
    assert cards[0].note_id == note_id
    assert cards[0].deck_id == default_deck.deck_id
    assert cards[0].template_ord == 0
    assert cards[0].status == "new"
    assert cards[0].due == TODAY


def test_create_basic_reverse_note_generates_two_cards(core_services):
    user_id = _create_user(core_services, "reverse")

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(2),
        fields=["front side", "back side"],
        tags=[],
        hint="",
        today=TODAY,
    )

    cards = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 2
    assert [card.template_ord for card in cards] == [0, 1]
    assert all(card.status == "new" for card in cards)
    assert all(card.due == TODAY for card in cards)


def test_create_cloze_note_generates_cards_from_cloze_ordinals(core_services):
    user_id = _create_user(core_services, "cloze")

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(3),
        fields=[
            "Paris is the {{c1::capital}} of {{c2::France}}.",
            "European geography",
        ],
        tags=["cloze"],
        hint="",
        today=TODAY,
    )

    cards = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 2
    assert [card.template_ord for card in cards] == [0, 1]


def test_update_cloze_note_reconciles_cards(core_services):
    user_id = _create_user(core_services, "cloze_update")

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(3),
        fields=[
            "Paris is the {{c1::capital}} of {{c2::France}}.",
            "European geography",
        ],
        tags=["cloze"],
        hint="",
        today=TODAY,
    )

    cards_before = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards_before) == 2
    assert [card.template_ord for card in cards_before] == [0, 1]

    updated_note_id = core_services.note.update_note(
        user_id=user_id,
        note_id=note_id,
        fields=[
            "Paris is the {{c1::capital}} of France.",
            "European geography",
        ],
        today=TODAY,
    )

    assert updated_note_id == note_id

    cards_after = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards_after) == 1
    assert cards_after[0].template_ord == 0


def test_duplicate_note_is_rejected_for_same_user(core_services):
    user_id = _create_user(core_services, "duplicate")

    core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(1),
        fields=["Question", "Answer"],
        tags=[],
        hint="",
        today=TODAY,
    )

    with pytest.raises(ValueError, match="duplicate"):
        core_services.note.create_note(
            user_id=user_id,
            note_type=get_note_type(1),
            fields=["Question", "Answer"],
            tags=[],
            hint="",
            today=TODAY,
        )


def test_same_note_content_is_allowed_for_different_users(core_services):
    user1_id = _create_user(core_services, "same_note_user1")
    user2_id = _create_user(core_services, "same_note_user2")

    user1_note_id = core_services.note.create_note(
        user_id=user1_id,
        note_type=get_note_type(1),
        fields=["Same Question", "Same Answer"],
        tags=[],
        hint="",
        today=TODAY,
    )

    user2_note_id = core_services.note.create_note(
        user_id=user2_id,
        note_type=get_note_type(1),
        fields=["Same Question", "Same Answer"],
        tags=[],
        hint="",
        today=TODAY,
    )

    assert user1_note_id != user2_note_id

    user1_cards = core_services.card.get_cards_by_note_id(user1_id, user1_note_id)
    user2_cards = core_services.card.get_cards_by_note_id(user2_id, user2_note_id)

    assert len(user1_cards) == 1
    assert len(user2_cards) == 1
    assert user1_cards[0].user_id == user1_id
    assert user2_cards[0].user_id == user2_id


def test_move_note_cards_to_another_deck(core_services):
    user_id = _create_user(core_services, "move_cards")

    custom_deck = core_services.deck.create_deck(
        Deck(
            user_id=user_id,
            deck_name="Custom Deck",
            deck_description="Deck for moved cards",
        )
    )

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(1),
        fields=["Move question", "Move answer"],
        tags=[],
        hint="",
        today=TODAY,
    )

    cards_before = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards_before) == 1
    assert cards_before[0].deck_id != custom_deck.deck_id

    result = core_services.deck.move_note_cards_to_deck(
        user_id=user_id,
        note_id=note_id,
        deck_id=custom_deck.deck_id,
    )

    assert result["moved_card_count"] == 1

    cards_after = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards_after) == 1
    assert cards_after[0].deck_id == custom_deck.deck_id


def test_delete_note_also_deletes_its_cards(core_services):
    user_id = _create_user(core_services, "delete_note")

    note_id = core_services.note.create_note(
        user_id=user_id,
        note_type=get_note_type(1),
        fields=["Delete question", "Delete answer"],
        tags=[],
        hint="",
        today=TODAY,
    )

    cards_before = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards_before) == 1

    result = core_services.note.delete_note(
        user_id=user_id,
        note_id=note_id,
    )

    assert result["deleted_note_count"] == 1
    assert result["deleted_card_count"] == 1

    with pytest.raises(ValueError):
        core_services.note.get_note(user_id, note_id)

    cards_after = core_services.card.get_cards_by_note_id(user_id, note_id)

    assert cards_after == []
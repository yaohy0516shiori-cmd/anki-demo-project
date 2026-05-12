from coreengine.note_type.type_registry import BASIC


def test_review_log_is_user_scoped(app_ctx):
    user1_id = app_ctx["user1_id"]
    user2_id = app_ctx["user2_id"]
    today = app_ctx["today"]

    deck = app_ctx["deck_repo"].get_default_deck(user1_id)

    note_id = app_ctx["note_service"].create_note(
        user_id=user1_id,
        note_type=BASIC,
        fields=["review-front", "review-back"],
        deck_id=deck.deck_id,
        today=today,
    )

    card = app_ctx["card_service"].get_cards_by_note_id(user1_id, note_id)[0]

    result = app_ctx["review_service"].review_card(
        user_id=user1_id,
        card_id=card.card_id,
        rating="good",
        today=today,
    )

    assert result["log"].user_id == user1_id

    logs_user1 = app_ctx["review_repo"].get_logs_by_card_id(user1_id, card.card_id)
    logs_user2 = app_ctx["review_repo"].get_logs_by_card_id(user2_id, card.card_id)

    assert len(logs_user1) == 1
    assert len(logs_user2) == 0


def test_delete_note_preserves_review_log(app_ctx):
    user1_id = app_ctx["user1_id"]
    today = app_ctx["today"]

    deck = app_ctx["deck_repo"].get_default_deck(user1_id)

    note_id = app_ctx["note_service"].create_note(
        user_id=user1_id,
        note_type=BASIC,
        fields=["log-front", "log-back"],
        deck_id=deck.deck_id,
        today=today,
    )

    card = app_ctx["card_service"].get_cards_by_note_id(user1_id, note_id)[0]

    app_ctx["review_service"].review_card(
        user_id=user1_id,
        card_id=card.card_id,
        rating="good",
        today=today,
    )

    assert app_ctx["review_repo"].count_logs_by_user_id(user1_id) == 1

    app_ctx["note_service"].delete_note(user1_id, note_id)

    assert app_ctx["review_repo"].count_logs_by_user_id(user1_id) == 1
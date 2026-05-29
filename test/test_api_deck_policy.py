# test api deck policy: create deck, update deck, delete deck
# default deck cannot be deleted, safe delete moves cards to default deck, hard delete deletes deck and cards


def test_default_deck_cannot_be_deleted(
    api_client,
    register_and_login,
    get_default_deck,
):
    account = register_and_login(prefix="deck")
    headers = account["headers"]

    default_deck = get_default_deck(headers)

    response = api_client.delete(
        f"/decks/{default_deck['deck_id']}",
        headers=headers,
    )

    assert response.status_code == 400
    assert "Default deck cannot be deleted" in response.text


def test_safe_delete_deck_moves_cards_to_default_deck(
    api_client,
    register_and_login,
    get_default_deck,
    create_basic_note,
):
    account = register_and_login(prefix="deck")
    headers = account["headers"]

    default_deck = get_default_deck(headers)

    create_deck_response = api_client.post(
        "/decks",
        headers=headers,
        json={
            "deck_name": "Temporary Deck",
            "deck_description": "to be deleted safely",
        },
    )
    assert create_deck_response.status_code == 200, create_deck_response.text

    custom_deck = create_deck_response.json()

    note = create_basic_note(
        headers=headers,
        deck_id=custom_deck["deck_id"],
        front="Safe delete question",
        back="Safe delete answer",
    )

    custom_cards_response = api_client.get(
        f"/decks/{custom_deck['deck_id']}/cards",
        headers=headers,
    )
    assert custom_cards_response.status_code == 200, custom_cards_response.text
    assert len(custom_cards_response.json()) == 1

    delete_response = api_client.delete(
        f"/decks/{custom_deck['deck_id']}",
        headers=headers,
    )
    assert delete_response.status_code == 200, delete_response.text

    delete_result = delete_response.json()
    assert delete_result["moved_card_count"] == 1
    assert delete_result["target_deck_id"] == default_deck["deck_id"]

    deleted_deck_response = api_client.get(
        f"/decks/{custom_deck['deck_id']}",
        headers=headers,
    )
    assert deleted_deck_response.status_code == 404

    default_cards_response = api_client.get(
        f"/decks/{default_deck['deck_id']}/cards",
        headers=headers,
    )
    assert default_cards_response.status_code == 200, default_cards_response.text

    default_cards = default_cards_response.json()
    assert len(default_cards) == 1
    assert default_cards[0]["note_id"] == note["note_id"]
    assert default_cards[0]["deck_id"] == default_deck["deck_id"]


def test_hard_delete_deck_deletes_cards(
    api_client,
    register_and_login,
    create_basic_note,
):
    account = register_and_login(prefix="harddeck")
    headers = account["headers"]

    create_deck_response = api_client.post(
        "/decks",
        headers=headers,
        json={
            "deck_name": "Hard Delete Deck",
            "deck_description": "cards should be deleted",
        },
    )
    assert create_deck_response.status_code == 200, create_deck_response.text

    custom_deck = create_deck_response.json()

    create_basic_note(
        headers=headers,
        deck_id=custom_deck["deck_id"],
        front="Hard delete question",
        back="Hard delete answer",
    )

    custom_cards_response = api_client.get(
        f"/decks/{custom_deck['deck_id']}/cards",
        headers=headers,
    )
    assert custom_cards_response.status_code == 200, custom_cards_response.text
    assert len(custom_cards_response.json()) == 1

    delete_response = api_client.delete(
        f"/decks/{custom_deck['deck_id']}",
        headers=headers,
        params={"hard": True},
    )
    assert delete_response.status_code == 200, delete_response.text

    delete_result = delete_response.json()
    assert delete_result["deleted_card_count"] == 1

    deleted_deck_response = api_client.get(
        f"/decks/{custom_deck['deck_id']}",
        headers=headers,
    )
    assert deleted_deck_response.status_code == 404
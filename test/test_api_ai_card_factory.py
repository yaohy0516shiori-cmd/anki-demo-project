def test_api_generate_and_confirm_ai_card_draft(
    api_client,
    register_and_login,
    get_default_deck,
):
    account = register_and_login(prefix="ai_factory")
    headers = account["headers"]

    default_deck = get_default_deck(headers)

    generate_response = api_client.post(
        "/ai/card-factory/drafts/generate",
        headers=headers,
        json={
            "source_text": "DNS translates domain names into IP addresses.",
            "user_prompt": "Make one basic flashcard.",
            "deck_id": default_deck["deck_id"],
            "note_type_id": 1,
            "max_cards": 1,
            "language": "en",
        },
    )

    assert generate_response.status_code == 200, generate_response.text

    batch = generate_response.json()
    assert batch["status"] == "pending"
    assert len(batch["items"]) == 1

    batch_id = batch["batch_id"]
    item_id = batch["items"][0]["item_id"]

    notes_before = api_client.get("/notes", headers=headers)
    assert notes_before.status_code == 200
    assert notes_before.json() == []

    confirm_response = api_client.post(
        f"/ai/card-factory/drafts/{batch_id}/confirm",
        headers=headers,
        json={
            "accepted_item_ids": [item_id],
            "rejected_item_ids": [],
        },
    )

    assert confirm_response.status_code == 200, confirm_response.text
    assert confirm_response.json()["created_note_count"] == 1

    notes_after = api_client.get("/notes", headers=headers)
    assert notes_after.status_code == 200
    assert len(notes_after.json()) == 1

    cards_response = api_client.get(
        f"/decks/{default_deck['deck_id']}/cards",
        headers=headers,
    )
    assert cards_response.status_code == 200
    assert len(cards_response.json()) == 1


def test_api_revise_ai_card_draft(
    api_client,
    register_and_login,
):
    account = register_and_login(prefix="ai_revise")
    headers = account["headers"]

    generate_response = api_client.post(
        "/ai/card-factory/drafts/generate",
        headers=headers,
        json={
            "source_text": "DNS translates domain names into IP addresses.",
            "user_prompt": "Make one basic flashcard.",
            "note_type_id": 1,
            "max_cards": 1,
            "language": "en",
        },
    )

    assert generate_response.status_code == 200, generate_response.text

    batch_id = generate_response.json()["batch_id"]

    revise_response = api_client.post(
        f"/ai/card-factory/drafts/{batch_id}/revise",
        headers=headers,
        json={
            "user_instruction": "Make the card shorter.",
            "language": "en",
        },
    )

    assert revise_response.status_code == 200, revise_response.text

    revised_batch = revise_response.json()
    latest = revised_batch["items"][0]["latest_version"]

    assert latest["version_no"] == 2
    assert "revised" in latest["tags"]
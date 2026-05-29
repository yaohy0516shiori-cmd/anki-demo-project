'''
stimulate (send-code, register, login, /me, list decks, create note, 
list deck cards, start study session, next, hint, 
back, rate, review logs, end session) flow step by step
register and login will be done in conftest.py
'''

def test_register_login_create_note_study_single_api_flow(
    api_client,
    register_and_login,
    get_default_deck,
    create_basic_note,
):
    account = register_and_login(prefix="single")
    headers = account["headers"]

    me_response = api_client.get("/users/me", headers=headers)
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["email"] == account["email"]

    default_deck = get_default_deck(headers)
    default_deck_id = default_deck["deck_id"]

    note = create_basic_note(
        headers=headers,
        deck_id=default_deck_id,
        front="Capital of France?",
        back="Paris",
        hint="capital city",
    )

    assert note["fields"] == ["Capital of France?", "Paris"]
    assert note["hint"] == "capital city"

    cards_response = api_client.get(
        f"/decks/{default_deck_id}/cards",
        headers=headers,
    )
    assert cards_response.status_code == 200, cards_response.text

    cards = cards_response.json()
    assert len(cards) == 1
    assert cards[0]["note_id"] == note["note_id"]

    start_response = api_client.post(
        "/study/sessions",
        headers=headers,
        json={"deck_id": default_deck_id},
    )
    assert start_response.status_code == 200, start_response.text

    session = start_response.json()
    assert session["deck_id"] == default_deck_id
    assert session["new_queue"] == 1

    session_id = session["session_id"]

    next_response = api_client.get(
        f"/study/sessions/{session_id}/next",
        headers=headers,
    )
    assert next_response.status_code == 200, next_response.text

    next_card = next_response.json()
    assert next_card["finished"] is False
    assert next_card["front"] == "Capital of France?"
    assert next_card["hint_available"] is True

    hint_response = api_client.post(
        f"/study/sessions/{session_id}/hint",
        headers=headers,
    )
    assert hint_response.status_code == 200, hint_response.text
    assert hint_response.json()["hint"] == "capital city"

    back_response = api_client.post(
        f"/study/sessions/{session_id}/back",
        headers=headers,
    )
    assert back_response.status_code == 200, back_response.text
    assert back_response.json()["back"] == "Paris"

    rate_response = api_client.post(
        f"/study/sessions/{session_id}/rate",
        headers=headers,
        json={"rating": "good"},
    )
    assert rate_response.status_code == 200, rate_response.text

    rate_result = rate_response.json()
    assert rate_result["card"]["reps"] == 1
    assert rate_result["review_log"]["rating"] == "good"
    assert rate_result["review_log"]["hint_used"] is True

    logs_response = api_client.get("/reviews", headers=headers)
    assert logs_response.status_code == 200, logs_response.text

    logs = logs_response.json()
    assert len(logs) == 1
    assert logs[0]["rating"] == "good"
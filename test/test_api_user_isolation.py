# test api user isolation: register, login, create note, study


def test_user_cannot_access_other_users_note(
    api_client,
    register_and_login,
    create_basic_note,
):
    user1 = register_and_login(prefix="user1")
    user2 = register_and_login(prefix="user2")

    note = create_basic_note(
        headers=user1["headers"],
        front="User1 question",
        back="User1 answer",
    )

    response = api_client.get(
        f"/notes/{note['note_id']}",
        headers=user2["headers"],
    )

    assert response.status_code == 404


def test_user_note_list_only_contains_own_notes(
    api_client,
    register_and_login,
    create_basic_note,
):
    user1 = register_and_login(prefix="user1")
    user2 = register_and_login(prefix="user2")

    user1_note = create_basic_note(
        headers=user1["headers"],
        front="User1 question",
        back="User1 answer",
    )

    user2_note = create_basic_note(
        headers=user2["headers"],
        front="User2 question",
        back="User2 answer",
    )

    user1_notes_response = api_client.get("/notes", headers=user1["headers"])
    assert user1_notes_response.status_code == 200, user1_notes_response.text

    user1_note_ids = {note["note_id"] for note in user1_notes_response.json()}

    assert user1_note["note_id"] in user1_note_ids
    assert user2_note["note_id"] not in user1_note_ids


def test_user_cannot_start_study_session_with_other_users_deck(
    api_client,
    register_and_login,
    get_default_deck,
):
    user1 = register_and_login(prefix="user1")
    user2 = register_and_login(prefix="user2")

    user1_default_deck = get_default_deck(user1["headers"])

    response = api_client.post(
        "/study/sessions",
        headers=user2["headers"],
        json={"deck_id": user1_default_deck["deck_id"]},
    )

    assert response.status_code == 400
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.deps import get_conn
from backend.app.main import app
from coreengine.storage.schema import init_db
from coreengine.storage.sqlite_connection import create_connection, close_connection


@pytest.fixture
def api_client(tmp_path: Path):
    db_path = tmp_path / "api_user_isolation.db"

    def override_get_conn():
        conn = create_connection(str(db_path))
        init_db(conn)
        try:
            yield conn
        finally:
            close_connection(conn)

    app.dependency_overrides[get_conn] = override_get_conn

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

def create_note_in_deck(
    api_client: TestClient,
    headers: dict[str, str],
    deck_id: int,
    front: str,
    back: str,
) -> int:
    response = api_client.post(
        "/notes",
        headers=headers,
        json={
            "note_type_id": 1,
            "fields": [front, back],
            "tags": [],
            "hint": "hint",
            "deck_id": deck_id,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["note_id"]

def register_and_login(
    api_client: TestClient,
    email: str,
    username: str,
    password: str,
) -> tuple[dict[str, str], int]:
    register_response = api_client.post(
        "/users/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )
    assert register_response.status_code == 200, register_response.text
    user_id = register_response.json()["user_id"]

    login_response = api_client.post(
        "/users/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id
    
def create_deck(api_client: TestClient, headers: dict[str, str], name: str) -> int:
    response = api_client.post(
        "/decks",
        headers=headers,
        json={
            "deck_name": name,
            "deck_description": f"{name} description",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["deck_id"]

def test_user_cannot_access_other_users_deck_by_id(api_client: TestClient):
    user1_headers, user1_id = register_and_login(
        api_client,
        "owner@example.com",
        "owner",
        "password123",
    )

    user1_deck_id = create_deck(
        api_client,
        user1_headers,
        "owner-private-deck",
    )

    create_note_in_deck(
        api_client,
        user1_headers,
        user1_deck_id,
        "owner front",
        "owner back",
    )

    user2_headers, user2_id = register_and_login(
        api_client,
        "viewer@example.com",
        "viewer",
        "password123",
    )

    assert user1_id != user2_id

    deck_response = api_client.get(
        f"/decks/{user1_deck_id}",
        headers=user2_headers,
    )
    assert deck_response.status_code == 404
    assert deck_response.json()["detail"] == "Deck not found"

    cards_response = api_client.get(
        f"/decks/{user1_deck_id}/cards",
        headers=user2_headers,
    )
    assert cards_response.status_code == 404
    assert cards_response.json()["detail"] == "Deck not found"
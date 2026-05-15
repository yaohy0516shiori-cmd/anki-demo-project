from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.deps import get_conn
from backend.app.main import app
from coreengine.storage.schema import init_db
from coreengine.storage.sqlite_connection import create_connection, close_connection


@pytest.fixture
def api_client(tmp_path: Path):
    db_path = tmp_path / "api_deck_policy.db"

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


def register_and_login(api_client: TestClient) -> dict[str, str]:
    register_response = api_client.post(
        "/users/register",
        json={
            "email": "deck-policy@example.com",
            "password": "testpassword",
            "username": "deck-policy-user",
        },
    )
    assert register_response.status_code == 200, register_response.text

    login_response = api_client.post(
        "/users/login",
        json={
            "email": "deck-policy@example.com",
            "password": "testpassword",
        },
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


def create_note_in_deck(
    api_client: TestClient,
    headers: dict[str, str],
    deck_id: int,
) -> int:
    response = api_client.post(
        "/notes",
        headers=headers,
        json={
            "note_type_id": 1,
            "fields": ["front", "back"],
            "tags": ["deck-policy"],
            "hint": "hint",
            "deck_id": deck_id,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["note_id"]


def get_default_deck_id(api_client: TestClient, headers: dict[str, str]) -> int:
    response = api_client.get("/decks", headers=headers)
    assert response.status_code == 200, response.text

    default_deck = next(deck for deck in response.json() if deck["is_default"] is True)
    return default_deck["deck_id"]


def test_soft_delete_moves_cards_to_default_deck(api_client: TestClient):
    headers = register_and_login(api_client)
    default_deck_id = get_default_deck_id(api_client, headers)

    deck_id = create_deck(api_client, headers, "soft-delete-deck")
    note_id = create_note_in_deck(api_client, headers, deck_id)

    cards_response = api_client.get(f"/decks/{deck_id}/cards", headers=headers)
    assert cards_response.status_code == 200, cards_response.text

    cards = cards_response.json()
    assert len(cards) == 1
    assert cards[0]["note_id"] == note_id
    assert cards[0]["deck_id"] == deck_id
    assert cards[0]["status"] == "new"

    delete_response = api_client.delete(f"/decks/{deck_id}", headers=headers)
    assert delete_response.status_code == 200, delete_response.text

    result = delete_response.json()
    assert result["message"] == f"deleted deck {deck_id} and moved 1 cards to default deck"
    assert result["moved_card_count"] == 1
    assert result["target_deck_id"] == default_deck_id

    default_cards_response = api_client.get(
        f"/decks/{default_deck_id}/cards",
        headers=headers,
    )
    assert default_cards_response.status_code == 200, default_cards_response.text

    default_cards = default_cards_response.json()
    assert len(default_cards) == 1
    assert default_cards[0]["note_id"] == note_id
    assert default_cards[0]["deck_id"] == default_deck_id


def test_hard_delete_deletes_deck_and_cards(api_client: TestClient):
    headers = register_and_login(api_client)

    deck_id = create_deck(api_client, headers, "hard-delete-deck")
    create_note_in_deck(api_client, headers, deck_id)

    cards_response = api_client.get(f"/decks/{deck_id}/cards", headers=headers)
    assert cards_response.status_code == 200, cards_response.text
    assert len(cards_response.json()) == 1

    delete_response = api_client.delete(
        f"/decks/{deck_id}?hard=true",
        headers=headers,
    )
    assert delete_response.status_code == 200, delete_response.text

    result = delete_response.json()
    assert result["message"] == f"deleted deck {deck_id} and 1 cards"
    assert result["deleted_card_count"] == 1

    decks_response = api_client.get("/decks", headers=headers)
    assert decks_response.status_code == 200, decks_response.text

    deck_ids = {deck["deck_id"] for deck in decks_response.json()}
    assert deck_id not in deck_ids


def test_default_deck_cannot_be_deleted(api_client: TestClient):
    headers = register_and_login(api_client)
    default_deck_id = get_default_deck_id(api_client, headers)

    delete_response = api_client.delete(
        f"/decks/{default_deck_id}",
        headers=headers,
    )
    assert delete_response.status_code == 400, delete_response.text
    assert delete_response.json()["detail"] == "Default deck cannot be deleted"

    hard_delete_response = api_client.delete(
        f"/decks/{default_deck_id}?hard=true",
        headers=headers,
    )
    assert hard_delete_response.status_code == 400, hard_delete_response.text
    assert hard_delete_response.json()["detail"] == "Default deck cannot be deleted"
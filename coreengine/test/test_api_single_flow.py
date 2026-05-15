# pathlib is a module for working with file paths.
from pathlib import Path
# pytest is a module for running tests.
import pytest
# fastapi.testclient is a module for testing FastAPI applications. it is a fake client that can be used to test the API.
from fastapi.testclient import TestClient
# backend.app.deps is a module for getting the database connection.
from backend.app.deps import get_conn
from backend.app.main import app
from coreengine.storage.schema import init_db
from coreengine.storage.sqlite_connection import create_connection, close_connection

# fixture for the API client. 调用时会自动调用这个函数拿到返回值。
@pytest.fixture
def api_client(tmp_path: Path):
    # create a temporary database for the API client.
    db_path = tmp_path / "api_single_flow.db"
    # override the get_conn function to use the temporary database.
    def override_get_conn():
        # create a connection to the database.
        conn = create_connection(str(db_path))
        # initialize the database.
        init_db(conn)
        # yield the connection to the test.
        try:
            yield conn
        finally:
            close_connection(conn)

    # override the get_conn function to use the temporary database.
    app.dependency_overrides[get_conn] = override_get_conn
    # create a test client for the API.

    with TestClient(app) as client:
        # yield the test client to the test.
        yield client

    # clear the dependency overrides.
    app.dependency_overrides.clear()


def test_register_login_create_note_study_single_api_flow(api_client: TestClient):
    # 1. API health check: verifies FastAPI app/router can start.
    health_response = api_client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"ok": True}

    # 2. Register: verifies /users/register -> UserService -> default deck creation.
    register_response = api_client.post(
        "/users/register",
        json={
            "email": "single-flow@example.com",
            "username": "single-flow-user",
            "password": "password123",
        },
    )
    assert register_response.status_code == 200, register_response.text
    user = register_response.json()
    assert user["user_id"] > 0
    assert user["email"] == "single-flow@example.com"

    # 3. Login: verifies password check and JWT creation.
    login_response = api_client.post(
        "/users/login",
        json={"email": "single-flow@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200, login_response.text
    token_data = login_response.json()
    assert token_data["access_token"]
    assert token_data["token_type"] == "bearer"

    auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # 4. Current user: verifies frontend token header can identify the user.
    me_response = api_client.get("/users/me", headers=auth_headers)
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["user_id"] == user["user_id"]

    # 5. Deck list: verifies default deck exists and is user-scoped.
    decks_response = api_client.get("/decks", headers=auth_headers)
    assert decks_response.status_code == 200, decks_response.text
    decks = decks_response.json()
    assert len(decks) >= 1
    default_deck = next(deck for deck in decks if deck["is_default"] is True)
    deck_id = default_deck["deck_id"]

    # 6. Create note: verifies /notes triggers NoteService and backend card generation.
    note_response = api_client.post(
        "/notes",
        headers=auth_headers,
        json={
            "note_type_id": 1,
            "fields": ["front-api-flow", "back-api-flow"],
            "tags": ["api", "single-flow"],
            "hint": "hint-api-flow",
            "deck_id": deck_id,
        },
    )
    assert note_response.status_code == 200, note_response.text
    note = note_response.json()
    assert note["fields"] == ["front-api-flow", "back-api-flow"]

    # 7. Deck cards: verifies generated card belongs to selected deck.
    cards_response = api_client.get(f"/decks/{deck_id}/cards", headers=auth_headers)
    assert cards_response.status_code == 200, cards_response.text
    cards = cards_response.json()
    assert len(cards) == 1
    card_id = cards[0]["card_id"]
    assert cards[0]["note_id"] == note["note_id"]
    assert cards[0]["status"] == "new"

    # 8. Start study: verifies /study/sessions builds queue from due cards.
    session_response = api_client.post(
        "/study/sessions",
        headers=auth_headers,
        json={"deck_id": deck_id},
    )
    assert session_response.status_code == 200, session_response.text
    session = session_response.json()
    assert session["deck_id"] == deck_id
    assert session["new_queue"] == 1
    session_id = session["session_id"]

    # 9. Next card: verifies service renders card front for frontend display.
    next_response = api_client.get(
        f"/study/sessions/{session_id}/next",
        headers=auth_headers,
    )
    assert next_response.status_code == 200, next_response.text
    next_card = next_response.json()
    assert next_card["finished"] is False
    assert next_card["front"] == "front-api-flow"
    assert next_card["card"]["card_id"] == card_id
    assert next_card["hint_available"] is True

    # 10. Hint/back/rate: verifies study actions mutate backend session/card/log state.
    hint_response = api_client.post(
        f"/study/sessions/{session_id}/hint",
        headers=auth_headers,
    )
    assert hint_response.status_code == 200, hint_response.text
    assert hint_response.json() == {"hint": "hint-api-flow"}

    back_response = api_client.post(
        f"/study/sessions/{session_id}/back",
        headers=auth_headers,
    )
    assert back_response.status_code == 200, back_response.text
    assert back_response.json() == {"back": "back-api-flow"}

    rate_response = api_client.post(
        f"/study/sessions/{session_id}/rate",
        headers=auth_headers,
        json={"rating": "good"},
    )
    assert rate_response.status_code == 200, rate_response.text
    rated = rate_response.json()
    assert rated["card"]["card_id"] == card_id
    assert rated["card"]["status"] in {"learning", "review"}
    assert rated["review_log"]["rating"] == "good"
    assert rated["review_log"]["hint_used"] is True

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.db import get_db
from backend.app.main import app
from coreengine.storage.schema import init_db
from coreengine.storage.sqlalchemy_connection import create_engine, close_connection
from coreengine.storage.sqlalchemy_models import Base

@pytest.fixture
def api_client():
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

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

def register_and_login(api_client: TestClient, email: str, username: str, password: str):
    code_response = api_client.post(
        "/users/register/send-code",
        json={"email": email},
    )
    assert code_response.status_code == 200, code_response.text
    verification_code = code_response.json()["dev_code"]

    register_response = api_client.post(
        "/users/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "verification_code": verification_code,
        },
    )
    assert register_response.status_code == 200, register_response.text

    login_response = api_client.post(
        "/users/login",
        json={
            "email": email,
            "password": password,
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
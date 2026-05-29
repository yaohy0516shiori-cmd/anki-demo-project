# 1. create test database engine
# 2. create session
# 3. Base.metadata.create_all(), create all tables
# 4. override FastAPI get_db
# 5. override or prepare email_code_service
# 6. clean up tables after tests

import os 
import uuid
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# setting test environment variables before import backend.app.main
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://memory_flashcards_user:memory_flashcards_password@localhost:5432/memory_flashcards_test"
)
os.environ.setdefault("TEST_REDIS_URL", "redis://localhost:6379/15")

from backend.app.main import app
from backend.app.db import get_db
from backend.app.deps import get_email_code_service
from backend.app.email_code_service import RedisEmailCodeService

from coreengine.storage.sqlalchemy_models import Base
from coreengine.storage.sqlalchemy_transaction import SqlAlchemyTransactionManager

from coreengine.storage.user_sqlalchemy_repo import SqlAlchemyUserRepository
from coreengine.storage.deck_sqlalchemy_repo import SqlAlchemyDeckRepository
from coreengine.storage.note_sqlalchemy_repo import SqlAlchemyNoteRepository
from coreengine.storage.card_sqlalchemy_repo import SqlAlchemyCardRepository
from coreengine.storage.reviewlog_sqlalchemy_repo import SqlAlchemyReviewLogRepository
from coreengine.storage.session_sqlalchemy_repo import SqlAlchemyStudySessionRepository

from coreengine.user.service import UserService
from coreengine.deck.service import DeckService
from coreengine.note.service import NoteService
from coreengine.card.service import CardService
from coreengine.reviewlogger.service import ReviewLoggerService
from coreengine.scheduler.simple_scheduler import Scheduler_v1
from coreengine.study.service import StudyService

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL")

if "test" not in TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL must contain 'test', got:", TEST_DATABASE_URL)

# create test Sqlalchemy engine, and only create once for all tests, close when all tests are done
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL,pool_pre_ping=True)
    yield engine
    engine.dispose()

# create a session factory for the test Sqlalchemy engine, and other tests can use this session factory to get a session
@pytest.fixture(scope="session")
def db_session_factory(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False)

# create a redis client for the test Redis, and only create once for all tests, close when all tests are done
@pytest.fixture(scope="session")
def redis_client():
    client = Redis.from_url(TEST_REDIS_URL,decode_responses=True)
    # ping the redis server to check if the connection is successful
    client.ping()
    yield client
    client.close()

# reset the test storage before each test, and clear the redis database, make sure the test is isolated
@pytest.fixture(autouse=True) # autouse=True means this fixture will be used automatically by pytest, no need to call it in the test function
def reset_test_storage(test_engine,redis_client):
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    redis_client.flushdb()

    yield
    redis_client.flushdb()
    Base.metadata.drop_all(test_engine)

# create isolated database session for each test, each test will get a new session, and close when the test is done
@pytest.fixture
def db_session(db_session_factory):
    db = db_session_factory()
    try:
        yield db
    finally:
        db.close()

# create a test client for the FastAPI app, and override the get_db and get_email_code_service dependencies
@pytest.fixture
def api_client(db_session_factory, redis_client):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_email_code_service():
        return RedisEmailCodeService(
            redis=redis_client,
            ttl_seconds=300,
            cooldown_seconds=60,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_email_code_service] = override_email_code_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# base on db_session, make up all core service instances like user_service, package them into a namespace for easy access in tests
@pytest.fixture
def core_services(db_session):
    transaction_manager = SqlAlchemyTransactionManager(db_session)

    user_repo = SqlAlchemyUserRepository(db_session)
    deck_repo = SqlAlchemyDeckRepository(db_session)
    note_repo = SqlAlchemyNoteRepository(db_session)
    card_repo = SqlAlchemyCardRepository(db_session)
    review_repo = SqlAlchemyReviewLogRepository(db_session)
    session_repo = SqlAlchemyStudySessionRepository(db_session)

    card_service = CardService(card_repo, note_repo, deck_repo)

    user_service = UserService(
        user_repo,
        deck_repo,
        transaction_manager,
    )

    deck_service = DeckService(
        deck_repo,
        card_service,
        transaction_manager,
    )

    note_service = NoteService(
        note_repo,
        card_service,
        deck_repo,
        transaction_manager,
    )

    review_service = ReviewLoggerService(
        card_repo,
        review_repo,
        Scheduler_v1(),
        transaction_manager,
    )

    study_service = StudyService(
        card_repo,
        review_service,
        note_repo,
        deck_repo,
        session_repo,
        transaction_manager,
    )

    return SimpleNamespace(
        user=user_service,
        deck=deck_service,
        note=note_service,
        card=card_service,
        review=review_service,
        study=study_service,
    )

# return a function that can register and login a user, and return the user's email, username, password, headers and user information
@pytest.fixture
def register_and_login(api_client):
    def _register_and_login(prefix: str = "user", password: str = "Password123"):
        unique = uuid.uuid4().hex[:8]
        email = f"{prefix}-{unique}@example.com"
        username = f"{prefix}_{unique}"

        send_code_response = api_client.post(
            "/users/register/send-code",
            json={"email": email},
        )
        assert send_code_response.status_code == 200, send_code_response.text

        dev_code = send_code_response.json()["dev_code"]
        assert dev_code is not None
        assert len(dev_code) == 6

        register_response = api_client.post(
            "/users/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "verification_code": dev_code,
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
        headers = {"Authorization": f"Bearer {token}"}

        me_response = api_client.get("/users/me", headers=headers)
        assert me_response.status_code == 200, me_response.text

        return {
            "email": email,
            "username": username,
            "password": password,
            "headers": headers,
            "user": me_response.json(),
        }

    return _register_and_login


# return a function that can get the default deck for the user
@pytest.fixture
def get_default_deck(api_client):
    def _get_default_deck(headers: dict):
        response = api_client.get("/decks", headers=headers)
        assert response.status_code == 200, response.text

        decks = response.json()
        default_decks = [deck for deck in decks if deck["is_default"] is True]

        assert len(default_decks) == 1
        return default_decks[0]

    return _get_default_deck


# return a function that can create a basic note for the user
@pytest.fixture
def create_basic_note(api_client):
    def _create_basic_note(
        headers: dict,
        deck_id: int | None = None,
        front: str = "Capital of France?",
        back: str = "Paris",
        hint: str = "capital city",
    ):
        payload = {
            "note_type_id": 1,
            "fields": [front, back],
            "tags": ["test"],
            "hint": hint,
        }

        if deck_id is not None:
            payload["deck_id"] = deck_id

        response = api_client.post(
            "/notes",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _create_basic_note
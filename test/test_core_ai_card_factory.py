from datetime import date
from types import SimpleNamespace

from backend.app.ai.fake_card_provider import FakeCardDraftProvider
from coreengine.ai_card_factory.service import AICardFactoryService
from coreengine.storage.ai_card_draft_sqlalchemy_repo import SqlAlchemyCardDraftRepository
from coreengine.storage.sqlalchemy_transaction import SqlAlchemyTransactionManager
from coreengine.storage.user_sqlalchemy_repo import SqlAlchemyUserRepository
from coreengine.storage.deck_sqlalchemy_repo import SqlAlchemyDeckRepository
from coreengine.storage.note_sqlalchemy_repo import SqlAlchemyNoteRepository
from coreengine.storage.card_sqlalchemy_repo import SqlAlchemyCardRepository
from coreengine.user.service import UserService
from coreengine.deck.service import DeckService
from coreengine.note.service import NoteService
from coreengine.card.service import CardService


TODAY = date(2026, 1, 1)


def _build_services(db_session):
    transaction_manager = SqlAlchemyTransactionManager(db_session)

    user_repo = SqlAlchemyUserRepository(db_session)
    deck_repo = SqlAlchemyDeckRepository(db_session)
    note_repo = SqlAlchemyNoteRepository(db_session)
    card_repo = SqlAlchemyCardRepository(db_session)
    draft_repo = SqlAlchemyCardDraftRepository(db_session)

    card_service = CardService(card_repo, note_repo, deck_repo)
    user_service = UserService(user_repo, deck_repo, transaction_manager)
    deck_service = DeckService(deck_repo, card_service, transaction_manager)
    note_service = NoteService(note_repo, card_service, deck_repo, transaction_manager)

    ai_card_factory = AICardFactoryService(
        draft_repo=draft_repo,
        draft_provider=FakeCardDraftProvider(),
        note_service=note_service,
        deck_repo=deck_repo,
        transaction_manager=transaction_manager,
    )

    return SimpleNamespace(
        user=user_service,
        deck=deck_service,
        note=note_service,
        card=card_service,
        ai_card_factory=ai_card_factory,
    )


def test_generate_draft_does_not_create_note_or_card(db_session):
    services = _build_services(db_session)

    user_id = services.user.register_user(
        email="ai-generate@example.com",
        username="ai_generate",
        password="Password123",
    )

    result = services.ai_card_factory.generate_drafts(
        user_id=user_id,
        source_text="DNS translates domain names into IP addresses.",
        note_type_id=1,
        max_cards=1,
    )

    batch = result["batch"]
    items = result["items"]

    assert batch.status == "pending"
    assert len(items) == 1
    assert items[0].item.status == "pending"
    assert services.note.list_notes(user_id) == []


def test_confirm_draft_creates_note_and_card(db_session):
    services = _build_services(db_session)

    user_id = services.user.register_user(
        email="ai-confirm@example.com",
        username="ai_confirm",
        password="Password123",
    )

    result = services.ai_card_factory.generate_drafts(
        user_id=user_id,
        source_text="DNS translates domain names into IP addresses.",
        note_type_id=1,
        max_cards=1,
    )

    batch_id = result["batch"].batch_id
    item_id = result["items"][0].item.item_id

    confirm_result = services.ai_card_factory.confirm_drafts(
        user_id=user_id,
        batch_id=batch_id,
        accepted_item_ids=[item_id],
        today=TODAY,
    )

    assert confirm_result["created_note_count"] == 1

    note_id = confirm_result["created_note_ids"][0]
    cards = services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 1
    assert cards[0].due == TODAY


def test_cloze_same_ordinal_multi_blank_creates_one_card(db_session):
    services = _build_services(db_session)

    user_id = services.user.register_user(
        email="ai-cloze@example.com",
        username="ai_cloze",
        password="Password123",
    )

    result = services.ai_card_factory.generate_drafts(
        user_id=user_id,
        source_text="photosynthesis",
        note_type_id=3,
        max_cards=1,
    )

    batch_id = result["batch"].batch_id
    item_id = result["items"][0].item.item_id

    confirm_result = services.ai_card_factory.confirm_drafts(
        user_id=user_id,
        batch_id=batch_id,
        accepted_item_ids=[item_id],
        today=TODAY,
    )

    note_id = confirm_result["created_note_ids"][0]
    cards = services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 1
    assert cards[0].template_ord == 0
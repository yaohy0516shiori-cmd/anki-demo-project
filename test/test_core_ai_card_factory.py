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
from coreengine.ai_card_factory.provider import GeneratedCardDraft

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

class TwoDraftsProvider:
    def generate_drafts(self, source_text: str, user_prompt: str, note_type_id: int | None, max_cards: int, language: str) -> list[GeneratedCardDraft]:
        return [
            GeneratedCardDraft(
                note_type_id=1,
                fields=["Front A", "Back A"],
                tags=["ai-generated", "a"],
                hint="hint-a",
                reason="first draft",
            ),
            GeneratedCardDraft(
                note_type_id=1,
                fields=["Front B", "Back B"],
                tags=["ai-generated", "b"],
                hint="hint-b",
                reason="second draft",
            ),
        ]
    
    def revise_drafts(self, current_drafts: list[GeneratedCardDraft], user_instruction: str, language: str) -> list[GeneratedCardDraft]:
        return current_drafts
    
class RevisionChangingProvider:
    def generate_drafts(
        self,
        source_text: str,
        user_prompt: str,
        note_type_id: int | None,
        max_cards: int,
        language: str,
    ) -> list[GeneratedCardDraft]:
        return [
            GeneratedCardDraft(
                note_type_id=1,
                fields=["Original front", "Original back"],
                tags=["ai-generated"],
                hint="old hint",
                reason="original draft",
            )
        ]

    def revise_drafts(
        self,
        current_drafts: list[GeneratedCardDraft],
        user_instruction: str,
        language: str,
    ) -> list[GeneratedCardDraft]:
        return [
            GeneratedCardDraft(
                note_type_id=1,
                fields=["Revised front", "Revised back"],
                tags=["ai-generated", "revised"],
                hint="new hint",
                reason=f"revised by: {user_instruction}",
            )
        ]

class InvalidClozeProvider:
    def generate_drafts(
        self,
        source_text: str,
        user_prompt: str,
        note_type_id: int | None,
        max_cards: int,
        language: str,
    ) -> list[GeneratedCardDraft]:
        return [
            GeneratedCardDraft(
                note_type_id=3,
                fields=[
                    "This is a cloze note but it has no cloze syntax.",
                    "extra",
                ],
                tags=["ai-generated"],
                hint="bad cloze",
                reason="invalid cloze test",
            )
        ]

    def revise_drafts(
        self,
        current_drafts: list[GeneratedCardDraft],
        user_instruction: str,
        language: str,
    ) -> list[GeneratedCardDraft]:
        return current_drafts

def _build_ai_services(db_session, provider):
    transaction_manager = SqlAlchemyTransactionManager(db_session)

    user_repo = SqlAlchemyUserRepository(db_session)
    deck_repo = SqlAlchemyDeckRepository(db_session)
    note_repo = SqlAlchemyNoteRepository(db_session)
    card_repo = SqlAlchemyCardRepository(db_session)
    draft_repo = SqlAlchemyCardDraftRepository(db_session)

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

    ai_card_factory = AICardFactoryService(
        draft_repo=draft_repo,
        draft_provider=provider,
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


def _create_user(services, prefix: str) -> int:
    return services.user.register_user(
        email=f"{prefix}@example.com",
        username=prefix,
        password="Password123",
    )

import pytest
def test_ai_card_draft_user_isolation(db_session):
    services=_build_ai_services(db_session,TwoDraftsProvider())

    user_a=_create_user(services, "user_a")
    user_b=_create_user(services, "user_b")
    result=services.ai_card_factory.generate_drafts(
        user_id=user_a,
        source_text="DNS translates domain names into IP addresses.",
        note_type_id=1,
        max_cards=2,
    )
    batch_id=result["batch"].batch_id
    item_ids=result["items"][0].item.item_id
    with pytest.raises(ValueError):
        services.ai_card_factory.confirm_drafts(
            user_id=user_b,
            batch_id=batch_id,
            accepted_item_ids=[item_ids],
            today=TODAY,
        )
    
    assert services.note.list_notes(user_b) == []
    assert services.note.list_notes(user_b) == []

    confirm_result = services.ai_card_factory.confirm_drafts(
        user_id=user_a,
        batch_id=batch_id,
        accepted_item_ids=[item_ids],
        rejected_item_ids=[],
        today=TODAY,
    )

    assert confirm_result["created_note_count"] == 1
    assert len(services.note.list_notes(user_a)) == 1
    assert services.note.list_notes(user_b) == []

def test_ai_card_draft_confirm_uses_latest_revised_version(db_session):
    services = _build_ai_services(db_session, RevisionChangingProvider())

    user_id = _create_user(services, "ai_revise_confirm")

    generate_result = services.ai_card_factory.generate_drafts(
        user_id=user_id,
        source_text="Original source",
        note_type_id=1,
        max_cards=1,
    )

    batch_id = generate_result["batch"].batch_id
    item_id = generate_result["items"][0].item.item_id

    revise_result = services.ai_card_factory.revise_drafts(
        user_id=user_id,
        batch_id=batch_id,
        user_instruction="Make it shorter and clearer.",
    )

    revised_item = revise_result["items"][0]

    assert revised_item.latest_version.version_no == 2
    assert revised_item.latest_version.fields == ["Revised front", "Revised back"]
    assert "revised" in revised_item.latest_version.tags
    assert revised_item.latest_version.hint == "new hint"

    confirm_result = services.ai_card_factory.confirm_drafts(
        user_id=user_id,
        batch_id=batch_id,
        accepted_item_ids=[item_id],
        rejected_item_ids=[],
        today=TODAY,
    )

    note_id = confirm_result["created_note_ids"][0]
    note = services.note.get_note(user_id, note_id)

    assert note.fields == ["Revised front", "Revised back"]
    assert note.tags == ["ai-generated", "revised"]
    assert note.hint == "new hint"

    cards = services.card.get_cards_by_note_id(user_id, note_id)

    assert len(cards) == 1

def test_ai_card_draft_rejected_item_is_not_created(db_session):
    services = _build_ai_services(db_session, TwoDraftsProvider())

    user_id = _create_user(services, "ai_reject_item")

    generate_result = services.ai_card_factory.generate_drafts(
        user_id=user_id,
        source_text="Two draft source",
        note_type_id=1,
        max_cards=2,
    )

    batch_id = generate_result["batch"].batch_id
    first_item_id = generate_result["items"][0].item.item_id
    second_item_id = generate_result["items"][1].item.item_id

    confirm_result = services.ai_card_factory.confirm_drafts(
        user_id=user_id,
        batch_id=batch_id,
        accepted_item_ids=[first_item_id],
        rejected_item_ids=[second_item_id],
        today=TODAY,
    )

    assert confirm_result["created_note_count"] == 1

    notes = services.note.list_notes(user_id)
    assert len(notes) == 1
    assert notes[0].fields == ["Front A", "Back A"]

    cards = services.card.get_cards_by_note_id(user_id, notes[0].note_id)
    assert len(cards) == 1

    batch_after_confirm = services.ai_card_factory.get_batch(user_id, batch_id)
    rows_by_id = {
        row.item.item_id: row
        for row in batch_after_confirm["items"]
    }

    assert rows_by_id[first_item_id].item.status == "created"
    assert rows_by_id[second_item_id].item.status == "rejected"
    assert batch_after_confirm["batch"].status == "confirmed"

def test_ai_card_draft_invalid_cloze_is_rejected_before_persistence(db_session):
    services = _build_ai_services(db_session, InvalidClozeProvider())

    user_id = _create_user(services, "ai_invalid_cloze")

    with pytest.raises(ValueError, match="cloze"):
        services.ai_card_factory.generate_drafts(
            user_id=user_id,
            source_text="Bad cloze source",
            note_type_id=3,
            max_cards=1,
        )

    assert services.note.list_notes(user_id) == []
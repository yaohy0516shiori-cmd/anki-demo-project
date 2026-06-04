
from typing import Generator
from backend.app.auth import decode_access_token
from fastapi import Depends, Header, HTTPException
from backend.app.email_code_service import RedisEmailCodeService
from backend.app.redis_client import get_redis_client
from backend.app.settings import get_settings,Settings
from redis import Redis
from sqlalchemy.orm import Session

from backend.app.db import get_db
from coreengine.storage.sqlalchemy_transaction import SqlAlchemyTransactionManager

from coreengine.storage.user_sqlalchemy_repo import SqlAlchemyUserRepository
from coreengine.storage.note_sqlalchemy_repo import SqlAlchemyNoteRepository
from coreengine.storage.card_sqlalchemy_repo import SqlAlchemyCardRepository
from coreengine.storage.deck_sqlalchemy_repo import SqlAlchemyDeckRepository
from coreengine.storage.reviewlog_sqlalchemy_repo import SqlAlchemyReviewLogRepository
from coreengine.storage.session_sqlalchemy_repo import SqlAlchemyStudySessionRepository

from coreengine.user.service import UserService
from coreengine.note.service import NoteService
from coreengine.card.service import CardService
from coreengine.deck.service import DeckService
from coreengine.reviewlogger.service import ReviewLoggerService
from coreengine.scheduler.simple_scheduler import Scheduler_v1
from coreengine.study.service import StudyService
from coreengine.storage.dashboard_query_repo import DashboardQueryRepository

from backend.app.ai.fake_card_provider import FakeCardDraftProvider
from coreengine.ai_card_factory.service import AICardFactoryService
from coreengine.storage.ai_card_draft_sqlalchemy_repo import SqlAlchemyCardDraftRepository
from backend.app.ai.ai_card_provider import OpenAICardDraftProvider
'''
CREATE DEPENDENCIES HERE: REPO, SERVICE, UTILITIES, ETC.
get_conn: get a connection to the database
get_transaction_manager: get a transaction manager
get_note_repo: get a note repository
get_card_repo: get a card repository
get_deck_repo: get a deck repository
get_review_repo: get a review repository
get_card_service: get a card service
get_note_service: get a note service
get_deck_service: get a deck service
get_review_service: get a review service
get_study_service: get a study service
get_current_user_id()
    从 HTTP Header 读取当前用户 ID
get_conn()
    每个请求创建 SQLite connection，请求结束后关闭
get_*_repo()
    给 repository 注入同一个 conn
get_*_service()
    给 service 注入 repo 和 transaction manager
get_session_repo()
    修掉之前 SESSION_REPO 全局错误
'''

def get_email_code_service(redis: Redis=Depends(get_redis_client),settings: Settings=Depends(get_settings)):
    return RedisEmailCodeService(
        redis=redis, 
        ttl_seconds=settings.email_code_ttl_seconds, 
        cooldown_seconds=settings.email_code_cooldown_seconds
        )
    
def get_transaction_manager(db: Session = Depends(get_db)):
    return SqlAlchemyTransactionManager(db)


def get_user_repo(db: Session = Depends(get_db)):
    return SqlAlchemyUserRepository(db)


def get_note_repo(db: Session = Depends(get_db)):
    return SqlAlchemyNoteRepository(db)


def get_card_repo(db: Session = Depends(get_db)):
    return SqlAlchemyCardRepository(db)


def get_deck_repo(db: Session = Depends(get_db)):
    return SqlAlchemyDeckRepository(db)


def get_review_repo(db: Session = Depends(get_db)):
    return SqlAlchemyReviewLogRepository(db)


def get_session_repo(db: Session = Depends(get_db)):
    return SqlAlchemyStudySessionRepository(db)

def get_dashboard_query_repo(db: Session = Depends(get_db)):
    return DashboardQueryRepository(db)

def get_user_service(
    user_repo=Depends(get_user_repo),
    deck_repo=Depends(get_deck_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return UserService(user_repo, deck_repo, transaction_manager)

def get_card_service(
    card_repo=Depends(get_card_repo),
    note_repo=Depends(get_note_repo),
    deck_repo=Depends(get_deck_repo)
):
    return CardService(card_repo, note_repo, deck_repo)


def get_note_service(
    note_repo=Depends(get_note_repo),
    card_service=Depends(get_card_service),
    deck_repo=Depends(get_deck_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return NoteService(note_repo, card_service, deck_repo, transaction_manager)


def get_deck_service(
    deck_repo=Depends(get_deck_repo),
    card_service=Depends(get_card_service),
    transaction_manager=Depends(get_transaction_manager),
):
    return DeckService(deck_repo, card_service, transaction_manager)


def get_review_service(
    card_repo=Depends(get_card_repo),
    review_repo=Depends(get_review_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    scheduler = Scheduler_v1()
    return ReviewLoggerService(card_repo, review_repo, scheduler, transaction_manager)

def get_study_service(
    card_repo=Depends(get_card_repo),
    review_service=Depends(get_review_service),
    note_repo=Depends(get_note_repo),
    deck_repo=Depends(get_deck_repo),
    session_repo=Depends(get_session_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return StudyService(card_repo, review_service, note_repo, deck_repo, session_repo, transaction_manager)

def get_current_user_id(authorization: str = Header(..., alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.removeprefix("Bearer ").strip()
    return decode_access_token(token)


def get_ai_card_draft_repo(db: Session = Depends(get_db)):
    return SqlAlchemyCardDraftRepository(db)


def get_ai_card_draft_provider(settings: Settings = Depends(get_settings)):
    if settings.ai_provider == "fake":
        return FakeCardDraftProvider()

    if settings.ai_provider == "openai":
        return OpenAICardDraftProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )

    raise ValueError("Unsupported AI provider")


def get_ai_card_factory_service(
    draft_repo=Depends(get_ai_card_draft_repo),
    draft_provider=Depends(get_ai_card_draft_provider),
    note_service=Depends(get_note_service),
    deck_repo=Depends(get_deck_repo),
    transaction_manager=Depends(get_transaction_manager),
):
    return AICardFactoryService(
        draft_repo=draft_repo,
        draft_provider=draft_provider,
        note_service=note_service,
        deck_repo=deck_repo,
        transaction_manager=transaction_manager,
    )
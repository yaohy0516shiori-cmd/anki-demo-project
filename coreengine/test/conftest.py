import pytest  # pytest 的 fixture 功能
from datetime import date  # 固定测试日期，避免测试受真实日期影响

from coreengine.storage.sqlite_connection import create_connection, close_connection, SqliteTransactionManager  # SQLite 连接和事务管理
from coreengine.storage.schema import init_db  # 初始化数据库表结构
from coreengine.storage.note_sqlite_repository import SqliteNoteRepository  # note 持久层
from coreengine.storage.card_sqlite_repository import SqliteCardRepository  # card 持久层
from coreengine.storage.deck_sqlite_repository import SqliteDeckRepository  # deck 持久层
from coreengine.storage.reviewlog_sqlite_repository import SqliteReviewLogRepository  # review log 持久层
from coreengine.study.inmemoryrepo import InMemoryStudySessionRepository  # 测试用内存 session 仓库

from coreengine.note.service import NoteService  # note 业务层
from coreengine.card.service import CardService  # card 业务层
from coreengine.deck.service import DeckService  # deck 业务层
from coreengine.reviewlogger.service import ReviewLoggerService  # review 业务层
from coreengine.study.service import StudyService  # study session 业务层
from coreengine.storage.user_sqlite_repository import SqliteUserRepository  # user 持久层
from coreengine.user.service import UserService  # user 业务层
from coreengine.scheduler.simple_scheduler import Scheduler_v1  # 调度器


@pytest.fixture
def app_ctx(tmp_path):
    db_path = tmp_path / "anki_test.db"  # 每个测试使用独立临时数据库
    conn = create_connection(str(db_path))  # 创建 SQLite 连接
    init_db(conn)  # 建表
    transaction_manager = SqliteTransactionManager(conn)  # 创建事务管理器

    user_repo = SqliteUserRepository(conn)  # user repo 使用同一个 conn
    note_repo = SqliteNoteRepository(conn)  # note repo 使用同一个 conn
    card_repo = SqliteCardRepository(conn)  # card repo 使用同一个 conn
    deck_repo = SqliteDeckRepository(conn)  # deck repo 使用同一个 conn
    review_repo = SqliteReviewLogRepository(conn)  # review log repo 使用同一个 conn
    session_repo = InMemoryStudySessionRepository()  # session 暂时用内存版，便于单元测试

    card_service = CardService(card_repo, note_repo, deck_repo)  # card service 需要 card/note/deck repo
    note_service = NoteService(note_repo, card_service, deck_repo, transaction_manager)  # note service 创建 note 后会生成 card
    deck_service = DeckService(deck_repo, card_service, transaction_manager)  # deck service 删除 deck 时会移动/删除 card
    user_service = UserService(user_repo, deck_repo, transaction_manager)  # user service 注册时会创建 default deck

    review_service = ReviewLoggerService(
        card_repo,  # review 时读取/更新 card
        review_repo,  # review 后写入 log
        Scheduler_v1(learning_steps=1, relearning_steps=1),  # 缩短测试流程
        transaction_manager=transaction_manager,  # card 更新和 log 写入放在同一事务
    )

    study_service = StudyService(
        card_repo=card_repo,  # study session 要取 due cards
        review_service=review_service,  # rate card 时调用 review service
        note_repo=note_repo,  # 渲染 card 时要读取 note
        deck_repo=deck_repo,  # start session 时校验 deck
        session_repo=session_repo,  # 保存 session 队列状态
        transaction_manager=transaction_manager,  # session 变更用事务保护
    )

    user1_id = user_service.register_user("user1@example.com", "user1", "password")  # 创建用户1，并自动创建默认 deck
    user2_id = user_service.register_user("user2@example.com", "user2", "password")  # 创建用户2，并自动创建默认 deck

    try:
        yield {
            "today": date(2026, 4, 22),  # 固定日期
            "conn": conn,  # 暴露连接，必要时检查底层数据库
            "user1_id": user1_id,  # 暴露用户1 id
            "user2_id": user2_id,  # 暴露用户2 id
            "user_service": user_service,  # 暴露 user service
            "note_repo": note_repo,  # 暴露 note repo
            "card_repo": card_repo,  # 暴露 card repo
            "deck_repo": deck_repo,  # 暴露 deck repo
            "review_repo": review_repo,  # 暴露 review repo
            "note_service": note_service,  # 暴露 note service
            "card_service": card_service,  # 暴露 card service
            "deck_service": deck_service,  # 暴露 deck service
            "review_service": review_service,  # 暴露 review service
            "study_service": study_service,  # 暴露 study service
        }
    finally:
        close_connection(conn)  # 测试结束关闭数据库连接
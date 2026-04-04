from datetime import date

from note.repository import InMemoryNoteRepository
from note.service import NoteService
from note_type.type_registry import BASIC
from card.repository import InMemoryCardRepository
from card.service import CardService
from reviewlogger.repository import ReviewLoggerRepository
from reviewlogger.service import ReviewLoggerService
from scheduler.simple_scheduler import Scheduler_v1
from study.service import StudyService


# 固定测试日期：
# 所有 create/review/session 都尽量用同一个 today，
# 避免系统当天和测试日期不一致导致“卡还没到期，session 取不到卡”。
TODAY = date(2026, 4, 3)


def build_app():
    """
    创建一套完整的 in-memory 测试环境。
    这里不依赖数据库，方便快速测 core engine 逻辑。
    """
    note_repo = InMemoryNoteRepository()
    card_repo = InMemoryCardRepository()
    card_service = CardService(card_repo)

    # 把 card_service 注入给 note_service，
    # 这样 create/update/delete note 时会自动同步 cards。
    note_service = NoteService(note_repo, card_service)

    review_repo = ReviewLoggerRepository()
    scheduler = Scheduler_v1()
    review_service = ReviewLoggerService(card_repo, review_repo, scheduler)

    study_service = StudyService(card_repo, review_service, note_repo)

    return {
        "note_repo": note_repo,
        "card_repo": card_repo,
        "card_service": card_service,
        "note_service": note_service,
        "review_repo": review_repo,
        "review_service": review_service,
        "scheduler": scheduler,
        "study_service": study_service,
    }


def create_basic_note_with_one_card(app, front="hello", back="你好"):
    """
    创建一条 BASIC note，并确保最终有 1 张 card。
    这里显式传 today=TODAY，保证新建 card 的 due 跟 session 用的是同一天。

    如果你后面确认 create_note -> reconcile_cards_for_note 已经完全稳定，
    fallback 也可以删掉。
    """
    note_service = app["note_service"]
    note_repo = app["note_repo"]
    card_service = app["card_service"]

    # 创建 note，并把 TODAY 传进去，保证 card.due = TODAY
    note_id = note_service.create_note(BASIC, [front, back], [], today=TODAY)

    # 正常情况：create_note 后应该已经自动生成 card
    cards = card_service.get_card_by_note_id(note_id)

    # fallback：
    # 如果当前某处同步逻辑还有问题，先手动补建 1 张 card，确保 study 流程能测。
    if len(cards) == 0:
        note = note_repo.get_note(note_id)
        card_service.create_cards_from_note(note, today=TODAY)
        cards = card_service.get_card_by_note_id(note_id)

    assert len(cards) == 1
    return note_id, cards[0]


def test_new_card_again_requeues_same_day():
    """
    测试场景：
    新卡 -> rate again -> due 仍然是 today -> 应该重新入队 -> 今天还能再次抽到这张卡
    """
    app = build_app()
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    # 启动一个固定 TODAY 的学习 session
    study_service.start_study_session(today=TODAY)

    # 第一次拿卡
    item = study_service.get_next_card()
    assert item is not None
    assert item["card"].card_id == first_card.card_id
    assert item["front"] == "hello"
    assert item["status"] == "new"

    # reveal 不影响当前卡，只是查看答案
    back = study_service.reveal_back_of_current_card()
    assert back == "你好"

    # 对新卡打 again
    result = study_service.rate_current_card("again")
    updated_card = result["card"]

    # 当前 scheduler 设计下：
    # new + again -> learning(step 0), due = today
    # 所以它今天仍然 eligible，会重新入队
    assert updated_card.card_id == first_card.card_id
    assert updated_card.status == "new"
    assert updated_card.due == TODAY
    assert updated_card.step_index == None
    assert updated_card.reps == 1

    # 再取下一张，应该还是同一张卡
    next_item = study_service.get_next_card()
    assert next_item is not None
    assert next_item["card"].card_id == first_card.card_id
    assert next_item["status"] == "new"

    # 本次评分应该写入 1 条 review log
    assert review_repo.count_logs() == 1


def test_continuous_learning_until_graduation():
    """
    测试场景：
    同一张新卡连续学习，反复入队，直到从 learning 毕业为 review。
    毕业后 due > today，不应再在今天继续出现。
    """
    app = build_app()
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    study_service.start_study_session(today=TODAY)

    seen_ids = []
    states_after_rating = []

    # 这部分依赖你当前 scheduler 的规则：
    # new + good -> learning(step 0)
    # learning 再连续 good 若干次 -> review(due tomorrow)
    #
    # 如果你后面改了 learning_steps 数量，这里的循环次数也要跟着改。
    for _ in range(5):
        item = study_service.get_next_card()
        assert item is not None

        # 整个连续学习流程里，应该一直是同一张卡在反复出现
        seen_ids.append(item["card"].card_id)
        assert item["card"].card_id == first_card.card_id
        assert item["front"] == "hello"

        # reveal 后再 rating，这是正确 reviewer 流程
        back = study_service.reveal_back_of_current_card()
        assert back == "你好"

        result = study_service.rate_current_card("good")
        updated_card = result["card"]

        states_after_rating.append(
            (updated_card.status, updated_card.step_index, updated_card.due)
        )

    # 第 1 次 good：new -> learning(step 0)
    assert states_after_rating[0][0] == "learning"
    assert states_after_rating[0][1] == 0
    assert states_after_rating[0][2] == TODAY

    # 中间几次：仍在 learning，step_index 递增
    assert states_after_rating[1][0] == "learning"
    assert states_after_rating[1][1] == 1
    assert states_after_rating[1][2] == TODAY

    assert states_after_rating[2][0] == "learning"
    assert states_after_rating[2][1] == 2
    assert states_after_rating[2][2] == TODAY

    assert states_after_rating[3][0] == "learning"
    assert states_after_rating[3][1] == 3
    assert states_after_rating[3][2] == TODAY

    # 最后一次 good：毕业进入 review，due 变成明天，不再重新入队
    assert states_after_rating[4][0] == "review"
    assert states_after_rating[4][1] is None
    assert states_after_rating[4][2] > TODAY

    # 今天应该已经没卡了
    assert study_service.get_next_card() is None
    assert study_service.is_finished() is True

    # 一共打了 5 次分，就应有 5 条日志
    assert review_repo.count_logs() == 5

    # 整个过程中，看到的都应该是同一张 card
    assert len(set(seen_ids)) == 1


def test_review_again_enters_relearning_and_requeues():
    """
    测试场景：
    已经是 review 的卡，在今天到期；
    如果打 again，应进入 relearning，并在今天重新入队。
    """
    app = build_app()
    study_service = app["study_service"]
    card_repo = app["card_repo"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    # 手动把这张卡改成 review 卡，模拟“以前学过，现在到期复习”
    review_card = card_repo.get_card(first_card.card_id)
    review_card.status = "review"
    review_card.due = TODAY
    review_card.interval = 3
    review_card.ease = 2.5
    review_card.reps = 10
    review_card.lapses = 0
    review_card.step_index = None
    card_repo.update_card(review_card)

    study_service.start_study_session(today=TODAY)

    item = study_service.get_next_card()
    assert item is not None
    assert item["card"].card_id == first_card.card_id
    assert item["status"] == "review"

    # 先 reveal，再评分
    back = study_service.reveal_back_of_current_card()
    assert back == "你好"

    result = study_service.rate_current_card("again")
    updated_card = result["card"]

    # review + again -> relearning(step 0), due=today, 应重新入队
    assert updated_card.status == "relearning"
    assert updated_card.step_index == 0
    assert updated_card.due == TODAY
    assert updated_card.interval == 0
    assert updated_card.lapses == 1
    assert updated_card.ease == 2.3  # 2.5 - 0.2

    # 继续拿下一张，应该还能拿到同一张卡
    next_item = study_service.get_next_card()
    assert next_item is not None
    assert next_item["card"].card_id == first_card.card_id
    assert next_item["status"] == "relearning"

    assert review_repo.count_logs() == 1


def test_invalid_flow():
    """
    测试非法调用流程：
    1. 没有当前卡时不能 reveal
    2. 没有当前卡时不能 rate
    3. 当前卡还没处理完时，不能直接 get 下一张
    """
    app = build_app()
    study_service = app["study_service"]

    create_basic_note_with_one_card(app)
    study_service.start_study_session(today=TODAY)

    # 没 get 就 reveal：应报错
    try:
        study_service.reveal_back_of_current_card()
        raise AssertionError("Expected ValueError when revealing without current card")
    except ValueError:
        pass

    # 没 get 就 rate：应报错
    try:
        study_service.rate_current_card("good")
        raise AssertionError("Expected ValueError when rating without current card")
    except ValueError:
        pass

    # 先 get 一张
    item = study_service.get_next_card()
    assert item is not None

    # 当前卡还没 reveal/rate 完成前，再 get 下一张：应报错
    try:
        study_service.get_next_card()
        raise AssertionError("Expected ValueError when getting next card too early")
    except ValueError:
        pass

    # 正常 reveal + rate 后，current card 才会释放
    back = study_service.reveal_back_of_current_card()
    assert back == "你好"
    study_service.rate_current_card("good")


def main():
    # 每个测试通过后打印一行，方便你知道卡在哪一步
    test_new_card_again_requeues_same_day()
    print("test_new_card_again_requeues_same_day passed")

    test_continuous_learning_until_graduation()
    print("test_continuous_learning_until_graduation passed")

    test_review_again_enters_relearning_and_requeues()
    print("test_review_again_enters_relearning_and_requeues passed")

    test_invalid_flow()
    print("test_invalid_flow passed")

    print("all tests passed")


if __name__ == "__main__":
    main()
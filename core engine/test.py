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


TODAY = date(2026, 4, 3)


def build_app():
    note_repo = InMemoryNoteRepository()
    card_repo = InMemoryCardRepository()
    card_service = CardService(card_repo)
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
    当前 create_note -> reconcile_cards 还有 bug 时，用这个 helper 兜底。
    等你修完 reconcile_cards 后，这个 fallback 可以删掉。
    """
    note_service = app["note_service"]
    note_repo = app["note_repo"]
    card_service = app["card_service"]

    note_id = note_service.create_note(BASIC, [front, back], [])

    cards = card_service.get_card_by_note_id(note_id)
    if len(cards) == 0:
        note = note_repo.get_note(note_id)
        card_service.create_cards_from_note(note)
        cards = card_service.get_card_by_note_id(note_id)

    assert len(cards) == 1
    return note_id, cards[0]


def test_new_card_again_requeues_same_day():
    app = build_app()
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    study_service.start_study_session(today=TODAY)

    item = study_service.get_next_card()
    assert item is not None
    assert item["card"].card_id == first_card.card_id
    assert item["front"] == "hello"
    assert item["status"] == "new"

    result = study_service.rate_current_card("again")
    updated_card = result["card"]

    # new + again -> still new, due today, so should re-enter queue
    assert updated_card.card_id == first_card.card_id
    assert updated_card.status == "new"
    assert updated_card.due == TODAY
    assert updated_card.step_index is None
    assert updated_card.reps == 1

    next_item = study_service.get_next_card()
    assert next_item is not None
    assert next_item["card"].card_id == first_card.card_id
    assert next_item["status"] == "new"

    assert review_repo.count_logs() == 1


def test_continuous_learning_until_graduation():
    app = build_app()
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    study_service.start_study_session(today=TODAY)

    seen_ids = []
    states_after_rating = []

    # 这套 scheduler 的规则：
    # new + good -> learning(step 0)
    # learning 再 good 4 次 -> review(due tomorrow)
    # 所以总共要打 5 次 good
    for _ in range(5):
        item = study_service.get_next_card()
        assert item is not None

        seen_ids.append(item["card"].card_id)
        assert item["card"].card_id == first_card.card_id
        assert item["front"] == "hello"

        result = study_service.rate_current_card("good")
        updated_card = result["card"]
        states_after_rating.append(
            (updated_card.status, updated_card.step_index, updated_card.due)
        )

    # 第 1 次：new -> learning step 0
    assert states_after_rating[0][0] == "learning"
    assert states_after_rating[0][1] == 0
    assert states_after_rating[0][2] == TODAY

    # 第 2,3,4 次：learning step 1,2,3
    assert states_after_rating[1][0] == "learning"
    assert states_after_rating[1][1] == 1
    assert states_after_rating[1][2] == TODAY

    assert states_after_rating[2][0] == "learning"
    assert states_after_rating[2][1] == 2
    assert states_after_rating[2][2] == TODAY

    assert states_after_rating[3][0] == "learning"
    assert states_after_rating[3][1] == 3
    assert states_after_rating[3][2] == TODAY

    # 第 5 次：graduate -> review, due tomorrow, no longer requeued today
    assert states_after_rating[4][0] == "review"
    assert states_after_rating[4][1] is None
    assert states_after_rating[4][2] > TODAY

    # 当前 session 今天应该已经没卡了
    assert study_service.get_next_card() is None
    assert study_service.is_finished() is True

    # 5 次评分，应该有 5 条 revlog
    assert review_repo.count_logs() == 5

    # 整个过程中，都是同一张卡在反复学习
    assert len(set(seen_ids)) == 1


def test_review_again_enters_relearning_and_requeues():
    app = build_app()
    study_service = app["study_service"]
    card_repo = app["card_repo"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    # 手动把卡设成 review，模拟“已经毕业过的复习卡”
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

    result = study_service.rate_current_card("again")
    updated_card = result["card"]

    # review + again -> relearning(step 0), due today, should requeue
    assert updated_card.status == "relearning"
    assert updated_card.step_index == 0
    assert updated_card.due == TODAY
    assert updated_card.interval == 0
    assert updated_card.lapses == 1
    assert updated_card.ease == 2.3  # 2.5 - 0.2

    next_item = study_service.get_next_card()
    assert next_item is not None
    assert next_item["card"].card_id == first_card.card_id
    assert next_item["status"] == "relearning"

    assert review_repo.count_logs() == 1


def main():
    test_new_card_again_requeues_same_day()
    print("test_new_card_again_requeues_same_day passed")

    test_continuous_learning_until_graduation()
    print("test_continuous_learning_until_graduation passed")

    test_review_again_enters_relearning_and_requeues()
    print("test_review_again_enters_relearning_and_requeues passed")

    print("all study session tests passed")


if __name__ == "__main__":
    main()
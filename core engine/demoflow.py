from datetime import date
from pprint import pprint

from note.repository import InMemoryNoteRepository
from note.service import NoteService
from note_type.type_registry import BASIC
from card.repository import InMemoryCardRepository
from card.service import CardService
from reviewlogger.repository import ReviewLoggerRepository
from reviewlogger.service import ReviewLoggerService
from scheduler.simple_scheduler import Scheduler_v1
from study.service import StudyService


# 固定 demo 日期，保证输出稳定、可复现
TODAY = date(2026, 4, 3)


def build_app():
    """
    创建一套 demo 用的 in-memory 应用环境。
    作用和 test 里的 build_app 类似，但这里主要用于打印过程，不是做 assert。
    """
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
        "study_service": study_service,
    }


def card_view(card):
    """
    把 Card 对象整理成更适合打印的字典。
    这样你能直观看到 card 当前状态，而不是一整坨对象信息。
    """
    return {
        "card_id": card.card_id,
        "note_id": card.note_id,
        "template_ord": card.template_ord,
        "status": card.status,
        "due": card.due,
        "interval": card.interval,
        "ease": card.ease,
        "reps": card.reps,
        "lapses": card.lapses,
        "step_index": card.step_index,
    }


def log_view(log):
    """
    把 ReviewLog 对象整理成清晰字典。
    重点看 old_* / new_* 的变化，这就是一条评分后状态变化的完整记录。
    """
    return {
        "log_id": log.log_id,
        "card_id": log.card_id,
        "rating": log.rating,
        "old_status": log.old_status,
        "new_status": log.new_status,
        "old_due": log.old_due,
        "new_due": log.new_due,
        "old_interval": log.old_interval,
        "new_interval": log.new_interval,
        "old_ease": log.old_ease,
        "new_ease": log.new_ease,
        "old_lapses": log.old_lapses,
        "new_lapses": log.new_lapses,
        "old_reps": log.old_reps,
        "new_reps": log.new_reps,
        "old_step_index": log.old_step_index,
        "new_step_index": log.new_step_index,
        "review_time": log.review_time,
    }


def main():
    app = build_app()

    # ---------------------------
    # 1. 创建一条 BASIC note
    # ---------------------------
    note_id = app["note_service"].create_note(
        BASIC,
        ["hello", "你好"],
        [],
        today=TODAY,
    )

    print("=== create note ===")
    print("input:")
    print({
        "note_type": "BASIC",
        "fields": ["hello", "你好"],
        "tags": [],
        "today": TODAY,
    })
    print("output:")
    print({"note_id": note_id})

    # 看看 note 创建后生成了哪些 cards
    cards = app["card_service"].get_card_by_note_id(note_id)
    print("\n=== cards after note creation ===")
    pprint([card_view(card) for card in cards])

    # ---------------------------
    # 2. 启动学习 session
    # ---------------------------
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    study_service.start_study_session(today=TODAY)

    print("\n=== start study session ===")
    print("input:")
    print({"today": TODAY})
    print("output:")
    print("session started")

    # ---------------------------
    # 3. 第一次 get：出 front
    # ---------------------------
    item = study_service.get_next_card()

    print("\n=== get_next_card() ===")
    print("input:")
    print("get_next_card()")
    print("output:")
    pprint({
        "card_id": item["card"].card_id,
        "front": item["front"],
        "status": item["status"],
        "step_index": item["step_index"],
    })

    # ---------------------------
    # 4. reveal：看答案
    # ---------------------------
    back = study_service.reveal_back_of_current_card()

    print("\n=== reveal_back_of_current_card() ===")
    print("input:")
    print("reveal_back_of_current_card()")
    print("output:")
    pprint({"back": back})

    # ---------------------------
    # 5. 第一次评分：good
    # ---------------------------
    result = study_service.rate_current_card("good")

    print("\n=== rate_current_card('good') ===")
    print("input:")
    print({"rating": "good"})
    print("updated card:")
    pprint(card_view(result["card"]))
    print("new review log:")
    pprint(log_view(result["log"]))

    # ---------------------------
    # 6. 再 get 一次：如果 due=today，应重新入队
    # ---------------------------
    item2 = study_service.get_next_card()

    print("\n=== get_next_card() again ===")
    print("input:")
    print("get_next_card()")
    print("output:")
    pprint({
        "card_id": item2["card"].card_id,
        "front": item2["front"],
        "status": item2["status"],
        "step_index": item2["step_index"],
    })

    # ---------------------------
    # 7. 再 reveal 一次
    # ---------------------------
    back2 = study_service.reveal_back_of_current_card()

    print("\n=== reveal_back_of_current_card() again ===")
    print("input:")
    print("reveal_back_of_current_card()")
    print("output:")
    pprint({"back": back2})

    # ---------------------------
    # 8. 第二次评分：again
    # ---------------------------
    result2 = study_service.rate_current_card("again")

    print("\n=== rate_current_card('again') ===")
    print("input:")
    print({"rating": "again"})
    print("updated card:")
    pprint(card_view(result2["card"]))
    print("new review log:")
    pprint(log_view(result2["log"]))

    # ---------------------------
    # 9. 打印仓库里的全部日志
    # ---------------------------
    print("\n=== all logs in repository ===")
    # 这里假设你的 review_repo 有 get_all_logs() 方法
    pprint([log_view(log) for log in review_repo.get_all_logs()])


if __name__ == "__main__":
    main()
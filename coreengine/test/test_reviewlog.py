from coreengine.test.test_basic import build_app, TODAY, create_basic_note_with_one_card


def test_reviewlog_records_first_transition_from_new_to_learning():
    """
    测试：
    新卡第一次打 good 后，
    revlog 是否正确记录：
    - old_status = new
    - new_status = learning
    - reps 从 0 -> 1
    - step_index 从 None -> 0
    """
    app = build_app()
    study_service = app["study_service"]
    review_repo = app["review_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    study_service.start_study_session(today=TODAY)

    item = study_service.get_next_card()
    assert item is not None
    assert item["card"].card_id == first_card.card_id

    study_service.reveal_back_of_current_card()
    result = study_service.rate_current_card("good")

    updated_card = result["card"]
    log = result["log"]

    # 当前 card 的新状态
    assert updated_card.status == "learning"
    assert updated_card.step_index == 0
    assert updated_card.reps == 1

    # log 里记录的 old/new 应与这次变化一致
    assert log.card_id == first_card.card_id
    assert log.rating == "good"
    assert log.old_status == "new"
    assert log.new_status == "learning"
    assert log.old_reps == 0
    assert log.new_reps == 1
    assert log.old_step_index is None
    assert log.new_step_index == 0
    assert log.old_due == TODAY
    assert log.new_due == TODAY

    # 仓库里应已有 1 条日志
    assert review_repo.count_logs() == 1


def test_reviewlog_history_accumulates_multiple_reviews():
    """
    测试：
    同一张卡连续评分两次后，
    review log history 应该有两条记录，且状态变化连续正确。
    """
    app = build_app()
    study_service = app["study_service"]
    review_service = app["review_service"]

    _, first_card = create_basic_note_with_one_card(app)

    study_service.start_study_session(today=TODAY)

    # 第一次：new -> learning(step 0)
    item = study_service.get_next_card()
    assert item is not None
    study_service.reveal_back_of_current_card()
    result1 = study_service.rate_current_card("good")
    log1 = result1["log"]

    # 第二次：learning(step 0) -> learning(step 1)
    item2 = study_service.get_next_card()
    assert item2 is not None
    study_service.reveal_back_of_current_card()
    result2 = study_service.rate_current_card("good")
    log2 = result2["log"]

    history = review_service.get_review_log_history(first_card.card_id)

    assert len(history) == 2

    # 第一条
    assert log1.old_status == "new"
    assert log1.new_status == "learning"
    assert log1.old_step_index is None
    assert log1.new_step_index == 0

    # 第二条
    assert log2.old_status == "learning"
    assert log2.new_status == "learning"
    assert log2.old_step_index == 0
    assert log2.new_step_index == 1

    # 从 history 里再检查一次，保证 repository 也正确存下来了
    history = sorted(history, key=lambda x: x.log_id)
    assert history[0].log_id == log1.log_id
    assert history[1].log_id == log2.log_id


def test_reviewlog_records_review_failure_into_relearning():
    """
    测试：
    把一张卡手动设成 review；
    在今天到期时打 again；
    应记录：
    - review -> relearning
    - lapses + 1
    - ease 降低
    """
    app = build_app()
    study_service = app["study_service"]
    card_repo = app["card_repo"]

    _, first_card = create_basic_note_with_one_card(app)

    # 先把卡改成 review 状态
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
    assert item["status"] == "review"

    study_service.reveal_back_of_current_card()
    result = study_service.rate_current_card("again")

    log = result["log"]
    updated_card = result["card"]

    # 当前 card 新状态
    assert updated_card.status == "relearning"
    assert updated_card.step_index == 0
    assert updated_card.lapses == 1
    assert updated_card.ease == 2.3

    # log 是否完整记录了 review -> relearning
    assert log.rating == "again"
    assert log.old_status == "review"
    assert log.new_status == "relearning"
    assert log.old_interval == 3
    assert log.new_interval == 0
    assert log.old_lapses == 0
    assert log.new_lapses == 1
    assert log.old_ease == 2.5
    assert log.new_ease == 2.3
    assert log.old_step_index is None
    assert log.new_step_index == 0


def main():
    test_reviewlog_records_first_transition_from_new_to_learning()
    print("test_reviewlog_records_first_transition_from_new_to_learning passed")

    test_reviewlog_history_accumulates_multiple_reviews()
    print("test_reviewlog_history_accumulates_multiple_reviews passed")

    test_reviewlog_records_review_failure_into_relearning()
    print("test_reviewlog_records_review_failure_into_relearning passed")

    print("all reviewlog tests passed")


if __name__ == "__main__":
    main()
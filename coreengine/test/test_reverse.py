from coreengine.test.test_basic import build_app, TODAY
from coreengine.note_type.type_registry import BASIC_REVERSE
from coreengine.render.card_render import render_card


def create_reverse_note_with_two_cards(app, front="apple", back="苹果"):
    """
    创建一条 BASIC_REVERSE note，并确认它生成两张 card。

    这里显式传 today=TODAY，
    保证新建 card 的 due 与 session 使用同一天。
    """
    note_service = app["note_service"]
    card_service = app["card_service"]

    note_id = note_service.create_note(
        BASIC_REVERSE,
        [front, back],
        [],
        today=TODAY,
    )

    cards = card_service.get_card_by_note_id(note_id)

    # basic_reverse 应该固定生成两张 card：
    # ord 0 -> 正向
    # ord 1 -> 反向
    assert len(cards) == 2
    return note_id, cards


def test_reverse_generates_two_cards_and_renders_both_directions():
    """
    测试：
    1. basic_reverse 是否生成两张 card
    2. 两张 card 的 template_ord 是否分别为 0 和 1
    3. render 是否一正一反
    """
    app = build_app()
    note_repo = app["note_repo"]

    note_id, cards = create_reverse_note_with_two_cards(app)
    note = note_repo.get_note(note_id)

    # 按 template_ord 排序，避免顺序不稳定
    cards = sorted(cards, key=lambda c: c.template_ord)

    assert cards[0].template_ord == 0
    assert cards[1].template_ord == 1

    rendered_0 = render_card(cards[0], note)
    rendered_1 = render_card(cards[1], note)

    # ord 0：正向
    assert rendered_0["front"] == "apple"
    assert rendered_0["back"] == "苹果"

    # ord 1：反向
    assert rendered_1["front"] == "苹果"
    assert rendered_1["back"] == "apple"


def test_reverse_second_card_appears_after_first_card_graduates():
    """
    测试：
    session 启动后，先出 ord 0；
    ord 0 这张卡毕业为 review 且 due > today 之后，
    下一张才会轮到 ord 1。

    为什么不能直接 get 两次？
    因为你当前 session 规则里：
    learning/relearning 队列优先级高于 new 队列，
    所以第一张卡只要今天还 eligible，就会反复先出现。
    """
    app = build_app()
    study_service = app["study_service"]

    note_id, cards = create_reverse_note_with_two_cards(app)
    cards = sorted(cards, key=lambda c: c.template_ord)

    first_card = cards[0]   # ord 0
    second_card = cards[1]  # ord 1

    study_service.start_study_session(today=TODAY)

    # 第一次拿到的应该是 ord 0
    item = study_service.get_next_card()
    assert item is not None
    assert item["card"].card_id == first_card.card_id
    assert item["front"] == "apple"

    # 当前 scheduler 里：
    # new + good -> learning(step 0)
    # 然后再经过若干次 good 才毕业为 review
    #
    # 这里用循环把第一张卡“学毕业”，
    # 这样它 due 会变成 tomorrow，就不会继续挡住第二张卡。
    for _ in range(5):
        # 第一次循环时，item 已经拿到了
        # 后面每次都要重新 get 一次当前卡
        if _ > 0:
            item = study_service.get_next_card()
            assert item["card"].card_id == first_card.card_id

        study_service.reveal_back_of_current_card()
        result = study_service.rate_current_card("good")

    updated_first = result["card"]
    assert updated_first.status == "review"
    assert updated_first.due > TODAY

    # 现在第一张卡已经毕业，下一张应该轮到 ord 1
    next_item = study_service.get_next_card()
    assert next_item is not None
    assert next_item["card"].card_id == second_card.card_id
    assert next_item["front"] == "苹果"


def main():
    test_reverse_generates_two_cards_and_renders_both_directions()
    print("test_reverse_generates_two_cards_and_renders_both_directions passed")

    test_reverse_second_card_appears_after_first_card_graduates()
    print("test_reverse_second_card_appears_after_first_card_graduates passed")

    print("all reverse tests passed")


if __name__ == "__main__":
    main()
from coreengine.test.test_basic import build_app, TODAY
from coreengine.note_type.type_registry import CLOZE
from coreengine.render.card_render import render_card


def create_cloze_note(app, text, back_extra="extra"):
    """
    创建一条 cloze note，并返回 note_id 和对应 cards。
    fields:
    - fields[0] = cloze text
    - fields[1] = back extra
    """
    note_service = app["note_service"]
    card_service = app["card_service"]

    note_id = note_service.create_note(
        CLOZE,
        [text, back_extra],
        [],
        today=TODAY,
    )
    cards = card_service.get_card_by_note_id(note_id)
    return note_id, cards


def test_cloze_generates_cards_and_renders_each_ordinal():
    """
    测试：
    1. 一条包含 c1 和 c2 的 cloze note 是否生成两张 card
    2. ord 0 / 1 的 front/back 是否正确
    """
    app = build_app()
    note_repo = app["note_repo"]

    text = "{{c1::Paris}} is in {{c2::France}}."
    note_id, cards = create_cloze_note(app, text, "city fact")

    assert len(cards) == 2

    # ord 0 -> c1
    # ord 1 -> c2
    cards = sorted(cards, key=lambda c: c.template_ord)
    assert cards[0].template_ord == 0
    assert cards[1].template_ord == 1

    note = note_repo.get_note(note_id)

    rendered_0 = render_card(cards[0], note)
    rendered_1 = render_card(cards[1], note)

    # 渲染 c1 时，front 隐藏 Paris，France 直接显示
    assert rendered_0["front"] == "[____] is in France."
    assert rendered_0["back"] == "Paris is in France.\n\ncity fact"

    # 渲染 c2 时，front 隐藏 France，Paris 直接显示
    assert rendered_1["front"] == "Paris is in [____]."
    assert rendered_1["back"] == "Paris is in France.\n\ncity fact"


def test_cloze_update_removes_missing_ord_and_preserves_existing_card():
    """
    测试：
    原来有 c1 和 c2；
    更新后只剩 c1；
    应该：
    - 保留 c1 那张旧 card
    - 删除 c2 那张 card
    """
    app = build_app()
    note_service = app["note_service"]
    card_service = app["card_service"]

    note_id, old_cards = create_cloze_note(
        app,
        "{{c1::Paris}} is in {{c2::France}}.",
        "geo",
    )

    old_cards = sorted(old_cards, key=lambda c: c.template_ord)
    old_c1 = old_cards[0]
    old_c2 = old_cards[1]

    # 更新后只剩 c1
    note_service.update_note(
        note_id,
        fields=["{{c1::Paris}} only.", "geo"],
        today=TODAY,
    )

    new_cards = sorted(card_service.get_card_by_note_id(note_id), key=lambda c: c.template_ord)

    # 只剩 1 张
    assert len(new_cards) == 1
    assert new_cards[0].template_ord == 0

    # 旧的 c1 card 应该保留，不应被重建
    assert new_cards[0].card_id == old_c1.card_id

    # c2 card 应该被删除
    remaining_ids = {card.card_id for card in new_cards}
    assert old_c2.card_id not in remaining_ids


def test_cloze_update_adds_new_ords_without_recreating_existing_one():
    """
    测试：
    原来只有 c1；
    更新后变成 c1、c2、c3；
    应该：
    - 原来的 c1 card 保留
    - 新增 c2、c3 两张 card
    """
    app = build_app()
    note_service = app["note_service"]
    card_service = app["card_service"]

    note_id, old_cards = create_cloze_note(
        app,
        "{{c1::Paris}} only.",
        "geo",
    )

    assert len(old_cards) == 1
    old_c1 = old_cards[0]

    # 更新成 c1 / c2 / c3
    note_service.update_note(
        note_id,
        fields=[
            "{{c1::Paris}} is in {{c2::France}} on {{c3::Earth}}.",
            "geo",
        ],
        today=TODAY,
    )

    new_cards = sorted(card_service.get_card_by_note_id(note_id), key=lambda c: c.template_ord)

    assert len(new_cards) == 3
    assert [card.template_ord for card in new_cards] == [0, 1, 2]

    # 原 c1 card 保留
    assert new_cards[0].card_id == old_c1.card_id

    # c2 / c3 是新卡，所以 id 应不同
    assert new_cards[1].card_id != old_c1.card_id
    assert new_cards[2].card_id != old_c1.card_id


def main():
    test_cloze_generates_cards_and_renders_each_ordinal()
    print("test_cloze_generates_cards_and_renders_each_ordinal passed")

    test_cloze_update_removes_missing_ord_and_preserves_existing_card()
    print("test_cloze_update_removes_missing_ord_and_preserves_existing_card passed")

    test_cloze_update_adds_new_ords_without_recreating_existing_one()
    print("test_cloze_update_adds_new_ords_without_recreating_existing_one passed")

    print("all cloze tests passed")


if __name__ == "__main__":
    main()
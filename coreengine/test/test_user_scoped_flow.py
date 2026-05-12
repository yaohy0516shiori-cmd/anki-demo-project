from datetime import timedelta  # 用来检查 review card 的 due 是否变成明天

from coreengine.deck.deckmodel import Deck  # 创建自定义 deck
from coreengine.note_type.type_registry import BASIC, BASIC_REVERSE, CLOZE  # 三种 note type


def test_register_creates_one_default_deck_per_user(app_ctx):
    user1_id = app_ctx["user1_id"]  # 取用户1 id
    user2_id = app_ctx["user2_id"]  # 取用户2 id

    user1_default = app_ctx["deck_repo"].get_default_deck(user1_id)  # 查用户1默认 deck
    user2_default = app_ctx["deck_repo"].get_default_deck(user2_id)  # 查用户2默认 deck

    assert user1_default.user_id == user1_id  # 用户1默认 deck 必须属于用户1
    assert user2_default.user_id == user2_id  # 用户2默认 deck 必须属于用户2
    assert user1_default.deck_id != user2_default.deck_id  # 两个用户不能共用同一个 deck
    assert user1_default.is_default is True  # 用户1有默认 deck 标记
    assert user2_default.is_default is True  # 用户2有默认 deck 标记


def test_password_hash_can_login_and_reject_wrong_password(app_ctx):
    user = app_ctx["user_service"].login("user1@example.com", "password")  # 正确密码应该能登录

    assert user.user_id == app_ctx["user1_id"]  # 登录返回的用户应该是 user1

    try:
        app_ctx["user_service"].login("user1@example.com", "wrong")  # 错误密码应该失败
    except ValueError as exc:
        assert "Invalid password" in str(exc)  # 确认失败原因是密码错误
    else:
        raise AssertionError("wrong password should not login")  # 如果没失败，说明认证有漏洞


def test_create_basic_note_uses_default_deck_when_deck_id_missing(app_ctx):
    user_id = app_ctx["user1_id"]  # 当前用户
    today = app_ctx["today"]  # 固定测试日期
    default_deck = app_ctx["deck_repo"].get_default_deck(user_id)  # 当前用户默认 deck

    note_id = app_ctx["note_service"].create_note(
        user_id=user_id,  # 多人隔离必须传 user_id
        note_type=BASIC,  # 创建 basic note
        fields=["front-basic", "back-basic"],  # basic 需要 front/back 两个字段
        hint="hint-basic",  # 添加提示
        today=today,  # 让新卡 due 固定为 today
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(user_id, note_id)  # 查这个 note 生成的 cards

    assert len(cards) == 1  # basic note 应该生成 1 张 card
    assert cards[0].user_id == user_id  # card 必须属于当前用户
    assert cards[0].deck_id == default_deck.deck_id  # 未传 deck_id 时进入默认 deck
    assert cards[0].status == "new"  # 新生成 card 状态是 new
    assert cards[0].due == today  # 新生成 card 今天可学


def test_users_cannot_see_each_others_cards(app_ctx):
    user1_id = app_ctx["user1_id"]  # 用户1
    user2_id = app_ctx["user2_id"]  # 用户2
    today = app_ctx["today"]  # 固定测试日期

    note_id = app_ctx["note_service"].create_note(
        user_id=user1_id,  # 用户1创建 note
        note_type=BASIC,  # basic note
        fields=["private-front", "private-back"],  # note 内容
        today=today,  # due 日期
    )

    assert len(app_ctx["card_service"].get_cards_by_note_id(user1_id, note_id)) == 1  # 用户1能查到自己的 card
    assert app_ctx["card_service"].get_cards_by_note_id(user2_id, note_id) == []  # 用户2查不到用户1的 card


def test_create_basic_reverse_generates_two_cards(app_ctx):
    user_id = app_ctx["user1_id"]  # 当前用户

    note_id = app_ctx["note_service"].create_note(
        user_id=user_id,  # 多人隔离
        note_type=BASIC_REVERSE,  # 正反双向卡
        fields=["front", "back"],  # front/back
        today=app_ctx["today"],  # 固定 due
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(user_id, note_id)  # 查询生成的 cards

    assert [card.template_ord for card in cards] == [0, 1]  # basic_reverse 应该生成两个模板：0 和 1


def test_update_cloze_note_reconciles_cards(app_ctx):
    user_id = app_ctx["user1_id"]  # 当前用户
    today = app_ctx["today"]  # 固定日期

    note_id = app_ctx["note_service"].create_note(
        user_id=user_id,  # 多人隔离
        note_type=CLOZE,  # cloze note
        fields=["I like {{c1::cats}} and {{c2::dogs}}", "extra"],  # 两个 cloze ord：c1/c2
        today=today,  # 固定 due
    )

    assert len(app_ctx["card_service"].get_cards_by_note_id(user_id, note_id)) == 2  # 初始应生成 2 张卡

    app_ctx["note_service"].update_note(
        user_id=user_id,  # 多人隔离
        note_id=note_id,  # 更新刚才的 note
        fields=["I like {{c1::cats}}", "extra"],  # 删除 c2，只保留 c1
        today=today,  # 新增卡时使用固定日期
    )

    cards = app_ctx["card_service"].get_cards_by_note_id(user_id, note_id)  # 重新查询 cards

    assert len(cards) == 1  # reconcile 后只剩 1 张 card
    assert cards[0].template_ord == 0  # c1 对应 template_ord 0


def test_study_session_pop_rate_reenqueue_and_review_log(app_ctx):
    user_id = app_ctx["user1_id"]  # 当前用户
    today = app_ctx["today"]  # 固定日期
    deck_id = app_ctx["deck_repo"].get_default_deck_id(user_id)  # 当前用户默认 deck

    app_ctx["note_service"].create_note(
        user_id=user_id,  # 多人隔离
        note_type=BASIC,  # basic note
        fields=["front-study", "back-study"],  # front/back
        hint="hint-study",  # hint
        today=today,  # due today
    )

    session_info = app_ctx["study_service"].start_study_session(user_id, deck_id, today=today)  # 开始学习 session
    session_id = session_info["session_id"]  # 保存 session id

    assert session_info["new_queue"] == 1  # 新卡队列应该有 1 张

    next_card = app_ctx["study_service"].get_next_card(user_id, session_id)  # 取下一张卡
    assert next_card["front"] == "front-study"  # front 渲染正确
    assert next_card["hint_available"] is True  # hint 可用

    assert app_ctx["study_service"].reveal_hint_of_current_card(user_id, session_id) == "hint-study"  # 展示 hint
    assert app_ctx["study_service"].reveal_back_of_current_card(user_id, session_id) == "back-study"  # 展示背面

    result1 = app_ctx["study_service"].rate_current_card(user_id, session_id, "good")  # 第一次 good
    assert result1["card"].status == "learning"  # new -> learning
    assert result1["log"].hint_used is True  # log 记录用过 hint

    app_ctx["study_service"].get_next_card(user_id, session_id)  # 重新取学习中的卡
    result2 = app_ctx["study_service"].rate_current_card(user_id, session_id, "good")  # 第二次 good

    assert result2["card"].status == "review"  # learning -> review
    assert result2["card"].due == today + timedelta(days=1)  # review 卡明天到期
    assert len(app_ctx["review_repo"].get_logs_by_card_id(user_id, result2["card"].card_id)) == 2  # 两次评分有两条 log
    assert app_ctx["study_service"].is_finished(user_id, session_id) is True  # 队列清空，session 完成
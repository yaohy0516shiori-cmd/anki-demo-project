from fastapi.testclient import TestClient

from backend.app import deps
from backend.app.main import app


def test_register_login_create_note_and_study_flow(tmp_path):
    # 1. 把测试数据库切到临时目录，避免污染真实数据库
    deps.DB_PATH = tmp_path / "api_test.db"

    # 2. 创建 FastAPI 测试客户端
    client = TestClient(app)

    # 3. 注册用户
    register_res = client.post(
        "/users/register",
        json={
            "email": "api@example.com",
            "username": "api",
            "password": "password",
        },
    )
    assert register_res.status_code == 200, register_res.text

    # 4. 登录用户
    login_res = client.post(
        "/users/login",
        json={
            "email": "api@example.com",
            "password": "password",
        },
    )
    assert login_res.status_code == 200, login_res.text

    # 5. 拿 token
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 6. 获取当前用户信息
    me_res = client.get("/users/me", headers=headers)
    assert me_res.status_code == 200, me_res.text

    # 7. 获取 deck 列表
    decks_res = client.get("/decks", headers=headers)
    assert decks_res.status_code == 200, decks_res.text

    default_deck = decks_res.json()[0]
    assert default_deck["is_default"] is True

    # 8. 创建 note
    note_res = client.post(
        "/notes",
        headers=headers,
        json={
            "note_type_id": 1,
            "fields": ["front", "back"],
            "hint": "hint",
        },
    )
    assert note_res.status_code == 200, note_res.text

    # 9. 开始学习 session
    session_res = client.post(
        "/study/sessions",
        headers=headers,
        json={"deck_id": default_deck["deck_id"]},
    )
    assert session_res.status_code == 200, session_res.text

    session_id = session_res.json()["session_id"]

    # 10. 获取下一张卡
    next_res = client.get(
        f"/study/sessions/{session_id}/next",
        headers=headers,
    )
    assert next_res.status_code == 200, next_res.text
    assert next_res.json()["front"] == "front"

    # 11. 查看 hint
    hint_res = client.post(
        f"/study/sessions/{session_id}/hint",
        headers=headers,
    )
    assert hint_res.status_code == 200, hint_res.text
    assert hint_res.json()["hint"] == "hint"

    # 12. 查看 back
    back_res = client.post(
        f"/study/sessions/{session_id}/back",
        headers=headers,
    )
    assert back_res.status_code == 200, back_res.text
    assert back_res.json()["back"] == "back"

    # 13. 评分
    rate_res = client.post(
        f"/study/sessions/{session_id}/rate",
        headers=headers,
        json={"rating": "good"},
    )
    assert rate_res.status_code == 200, rate_res.text
    assert rate_res.json()["card"]["status"] == "learning"
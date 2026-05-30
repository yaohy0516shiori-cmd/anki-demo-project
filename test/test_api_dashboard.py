from datetime import date


def test_dashboard_card_pagination_filter_and_search(
    api_client,
    register_and_login,
    get_default_deck,
    create_basic_note,
):
    account = register_and_login(prefix="dashboard")
    headers = account["headers"]
    default_deck = get_default_deck(headers)
    deck_id = default_deck["deck_id"]

    create_basic_note(headers=headers, deck_id=deck_id, front="Capital of France?", back="Paris")
    create_basic_note(headers=headers, deck_id=deck_id, front="Capital of Germany?", back="Berlin")
    create_basic_note(headers=headers, deck_id=deck_id, front="Capital of Japan?", back="Tokyo")

    page_response = api_client.get(
        f"/dashboard/decks/{deck_id}/cards",
        headers=headers,
        params={"page": 1, "page_size": 2, "sort": "created_asc"},
    )
    assert page_response.status_code == 200, page_response.text

    page = page_response.json()
    assert page["page"] == 1
    assert page["page_size"] == 2
    assert page["total"] == 3
    assert page["total_pages"] == 2
    assert len(page["items"]) == 2

    search_response = api_client.get(
        f"/dashboard/decks/{deck_id}/cards",
        headers=headers,
        params={"q": "Berlin"},
    )
    assert search_response.status_code == 200, search_response.text

    search_page = search_response.json()
    assert search_page["total"] == 1
    assert "Berlin" in search_page["items"][0]["content"]

    status_response = api_client.get(
        f"/dashboard/decks/{deck_id}/cards",
        headers=headers,
        params={"status": "new"},
    )
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["total"] == 3


def test_dashboard_summary_and_deck_stats_after_review(
    api_client,
    register_and_login,
    get_default_deck,
    create_basic_note,
):
    account = register_and_login(prefix="stats")
    headers = account["headers"]
    default_deck = get_default_deck(headers)
    deck_id = default_deck["deck_id"]

    create_basic_note(headers=headers, deck_id=deck_id, front="Reviewed question", back="Reviewed answer")
    create_basic_note(headers=headers, deck_id=deck_id, front="Unreviewed question", back="Unreviewed answer")

    start_response = api_client.post(
        "/study/sessions",
        headers=headers,
        json={"deck_id": deck_id, "today": date.today().isoformat()},
    )
    assert start_response.status_code == 200, start_response.text
    session_id = start_response.json()["session_id"]

    next_response = api_client.get(f"/study/sessions/{session_id}/next", headers=headers)
    assert next_response.status_code == 200, next_response.text

    back_response = api_client.post(f"/study/sessions/{session_id}/back", headers=headers)
    assert back_response.status_code == 200, back_response.text

    rate_response = api_client.post(
        f"/study/sessions/{session_id}/rate",
        headers=headers,
        json={"rating": "good"},
    )
    assert rate_response.status_code == 200, rate_response.text

    summary_response = api_client.get("/dashboard/summary", headers=headers)
    assert summary_response.status_code == 200, summary_response.text
    summary = summary_response.json()
    assert summary["total_decks"] == 1
    assert summary["total_notes"] == 2
    assert summary["total_cards"] == 2
    assert summary["total_reviews"] == 1
    assert summary["good_reviews"] == 1
    assert summary["again_reviews"] == 0
    assert summary["good_rate"] == 1.0

    deck_stats_response = api_client.get("/dashboard/decks", headers=headers)
    assert deck_stats_response.status_code == 200, deck_stats_response.text
    deck_stats = deck_stats_response.json()
    assert len(deck_stats) == 1
    assert deck_stats[0]["deck_id"] == deck_id
    assert deck_stats[0]["card_count"] == 2
    assert deck_stats[0]["review_log_count"] == 1
    assert deck_stats[0]["good_count"] == 1

    daily_response = api_client.get(
        "/dashboard/reviews/daily",
        headers=headers,
        params={"days": 7},
    )
    assert daily_response.status_code == 200, daily_response.text
    daily = daily_response.json()
    assert len(daily) == 7
    assert daily[-1]["review_count"] == 1
    assert daily[-1]["good_count"] == 1


def test_dashboard_does_not_expose_other_users_deck(
    api_client,
    register_and_login,
    get_default_deck,
):
    user1 = register_and_login(prefix="dashuser1")
    user2 = register_and_login(prefix="dashuser2")
    user1_default_deck = get_default_deck(user1["headers"])

    response = api_client.get(
        f"/dashboard/decks/{user1_default_deck['deck_id']}/cards",
        headers=user2["headers"],
    )

    assert response.status_code == 400
    assert "Deck not found" in response.text

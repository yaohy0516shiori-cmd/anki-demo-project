from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.deps import get_dashboard_query_repo, get_current_user_id
from backend.schemas.dashboard import (
    DailyReviewStatsOut,
    DeckLearningStatsOut,
    DashboardCardPageOut,
    DashboardSummaryOut)
from coreengine.storage.dashboard_query_repo import DashboardQueryRepository
router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryOut)
def get_summary(
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    return repo.get_summary_stats(user_id)

@router.get("/decks", response_model=list[DeckLearningStatsOut])
def get_decks_stats(
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    return repo.get_decks_stats(user_id)

@router.get("/decks/{deck_id}/cards", response_model=DashboardCardPageOut)
def get_deck_cards(
    deck_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    status: str | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    sort: str = Query("due_asc", regex=r"^(due_asc|due_desc|created_asc|created_desc|reps_desc|lapses_desc)$"),
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.list_deck_cards(user_id, deck_id, page, page_size, q, status, due_before, due_after, sort)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reviews/daily", response_model=list[DailyReviewStatsOut])
def get_daily_review_stats(
    days: int = Query(14, ge=1, le=365),
    deck_id: int | None = None,
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.get_daily_review_stats(user_id, days, deck_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
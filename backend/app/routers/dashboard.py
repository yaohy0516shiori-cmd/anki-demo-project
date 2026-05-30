from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.deps import get_dashboard_query_repo, get_current_user_id
from backend.schemas.dashboard import (
    DailyReviewStatsOut,
    DeckLearningStatsOut,
    DashboardCardPageOut,
    DashboardSummaryOut,
    DueForecastStatsOut,
    PeriodReviewStatsOut,
    )
from coreengine.storage.dashboard_query_repo import DashboardQueryRepository
router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryOut)
def get_summary(
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
    today: date | None = None,
):
    today = today if today is not None else date.today()
    return repo.get_summary_stats(user_id=user_id, today=today)

@router.get("/decks", response_model=list[DeckLearningStatsOut])
def get_decks_stats(
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
    today: date | None = None,
):
    today = today if today is not None else date.today()
    return repo.get_decks_stats(user_id=user_id, today=today)

@router.get("/decks/{deck_id}/cards", response_model=DashboardCardPageOut)
def get_deck_cards(
    deck_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    status: str | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    sort: str = Query("due_asc", pattern=r"^(due_asc|due_desc|created_asc|created_desc|reps_desc|lapses_desc)$"),
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.list_deck_cards(
            user_id = user_id, 
            deck_id = deck_id, 
            page = page, 
            page_size = page_size, 
            q = q, 
            status = status, 
            due_before = due_before, 
            due_after = due_after, 
            sort = sort)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cards/search", response_model=DashboardCardPageOut)
def search_cards(
    q: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    deck_id: int | None = None,
    status: str | None = Query(None, pattern="^(new|learning|review|relearning)$",),
    due_before: date | None = None,
    due_after: date | None = None,
    sort: str = Query("due_asc", pattern=r"^(due_asc|due_desc|created_asc|created_desc|reps_desc|lapses_desc)$"),
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.search_cards(
            user_id=user_id, 
            q=q, 
            page=page, 
            deck_id=deck_id,
            page_size=page_size, 
            status=status, 
            due_before=due_before,
            due_after=due_after,
            sort=sort,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reviews/daily", response_model=list[DailyReviewStatsOut])
def get_daily_review_stats(
    days: int = Query(14, ge=1, le=365),
    deck_id: int | None = None,
    today: date | None = None,
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        today = today if today is not None else date.today()
        return repo.get_daily_review_stats(user_id=user_id, days=days, deck_id=deck_id, today=today)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cards/due-forecast", response_model=list[DueForecastStatsOut])
def get_due_forecast_stats(
    days: int = Query(7, ge=1, le=31),
    deck_id: int | None = None,
    today: date | None = None,
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        today = today if today is not None else date.today()
        return repo.get_due_forecast_stats(user_id=user_id, days=days, deck_id=deck_id, today=today)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reviews/monthly", response_model=list[PeriodReviewStatsOut])
def get_monthly_review_stats(
    year: int,
    month: int = Query(..., ge=1, le=12),
    deck_id: int | None = None,
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.get_monthly_review_stats(user_id=user_id, year=year, month=month, deck_id=deck_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reviews/yearly", response_model=list[PeriodReviewStatsOut])
def get_yearly_review_stats(
    year: int,
    deck_id: int | None = None,
    repo: DashboardQueryRepository = Depends(get_dashboard_query_repo),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return repo.get_yearly_review_stats(user_id=user_id, year=year, deck_id=deck_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
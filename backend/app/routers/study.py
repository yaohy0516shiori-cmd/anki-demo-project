from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.deps import get_study_service, get_current_user_id

'''
CREATE ROUTERS HERE: API ENDPOINTS FOR STUDY, HTTP REQUESTS, ETC.
'''
router = APIRouter()


class StudySessionStart(BaseModel):
    deck_id: int
    today: date | None = None


class StudyRating(BaseModel):
    rating: str


@router.post("/sessions")
def start_session(payload: StudySessionStart, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        return study_service.start_study_session(
            user_id=user_id,
            deck_id=payload.deck_id,
            today=payload.today,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/next")
def get_next_card(session_id: str, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        result = study_service.get_next_card(user_id, session_id)
        if result is None:
            return {"finished": True}
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/hint")
def reveal_hint(session_id: str, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        return {"hint": study_service.reveal_hint_of_current_card(user_id, session_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/back")
def reveal_back(session_id: str, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        return {"back": study_service.reveal_back_of_current_card(user_id, session_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/rate")
def rate_current_card(
    session_id: str,
    payload: StudyRating,
    study_service=Depends(get_study_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return study_service.rate_current_card(user_id, session_id, payload.rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/status")
def session_status(session_id: str, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        return {"finished": study_service.is_finished(user_id, session_id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.deps import get_study_service

router = APIRouter()


class StudySessionStart(BaseModel):
    deck_id: int
    today: date | None = None


class StudyRating(BaseModel):
    rating: str


@router.post("/sessions")
def start_session(payload: StudySessionStart, study_service=Depends(get_study_service)):
    try:
        return study_service.start_study_session(
            deck_id=payload.deck_id,
            today=payload.today,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/next")
def get_next_card(session_id: str, study_service=Depends(get_study_service)):
    try:
        result = study_service.get_next_card(session_id)
        if result is None:
            return {"finished": True}
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/hint")
def reveal_hint(session_id: str, study_service=Depends(get_study_service)):
    try:
        return {"hint": study_service.reveal_hint_of_current_card(session_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/back")
def reveal_back(session_id: str, study_service=Depends(get_study_service)):
    try:
        return {"back": study_service.reveal_back_of_current_card(session_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sessions/{session_id}/rate")
def rate_current_card(
    session_id: str,
    payload: StudyRating,
    study_service=Depends(get_study_service),
):
    try:
        return study_service.rate_current_card(session_id, payload.rating)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/status")
def session_status(session_id: str, study_service=Depends(get_study_service)):
    try:
        return {"finished": study_service.is_finished(session_id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
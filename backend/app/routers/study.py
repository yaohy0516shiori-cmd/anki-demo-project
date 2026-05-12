from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.schemas.study import (
    StudySessionStart,
    StudyRating,
    StudySessionStartOut,
    StudyNextOut,
)
from backend.app.deps import get_study_service, get_current_user_id

'''
CREATE ROUTERS HERE: API ENDPOINTS FOR STUDY, HTTP REQUESTS, ETC.
'''
router = APIRouter()

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


@router.get("/sessions/{session_id}/next", response_model=StudyNextOut)
def get_next_card(
    session_id: str,
    study_service=Depends(get_study_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        # 调用核心学习服务，尝试取下一张卡
        result = study_service.get_next_card(user_id, session_id)

        # result is None 表示当前 session 没有下一张卡了
        if result is None:
            return {
                "finished": True,          # 告诉前端：学习完成
                "user_id": user_id,        # 当前用户 id
                "session_id": session_id,  # 当前 session id
                "card": None,              # 没有当前卡
                "note": None,              # 没有当前 note
                "front": None,             # 没有正面内容
                "status": None,            # 没有卡片状态
                "step_index": None,        # 没有学习步骤
                "deck_id": None,           # 没有当前 deck/card 对应值
                "hint_available": False,   # 没有卡，所以没有 hint
            }

        # 有下一张卡时，也补上 finished=False
        return {
            "finished": False,  # 告诉前端：还有卡，继续显示卡片
            **result,           # 保留原来 service 返回的 user_id/session_id/card/note/front 等数据
        }

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

def card_to_dict(card):
    return card.to_dict()


def review_log_to_dict(log):
    return {
        "user_id": log.user_id,
        "review_log_id": log.review_log_id,
        "card_id": log.card_id,
        "deck_id": log.deck_id,
        "note_id": log.note_id,
        "rating": log.rating,
        "old_status": log.old_status,
        "new_status": log.new_status,
        "old_due": log.old_due.isoformat() if hasattr(log.old_due, "isoformat") else log.old_due,
        "new_due": log.new_due.isoformat() if hasattr(log.new_due, "isoformat") else log.new_due,
        "old_interval": log.old_interval,
        "new_interval": log.new_interval,
        "old_ease": log.old_ease,
        "new_ease": log.new_ease,
        "old_lapses": log.old_lapses,
        "new_lapses": log.new_lapses,
        "old_reps": log.old_reps,
        "new_reps": log.new_reps,
        "old_step_index": log.old_step_index,
        "new_step_index": log.new_step_index,
        "hint_used": log.hint_used,
        "review_time": log.review_time,
    }

@router.post("/sessions/{session_id}/rate")
def rate_current_card(
    session_id: str,
    payload: StudyRating,
    study_service=Depends(get_study_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        result = study_service.rate_current_card(user_id, session_id, payload.rating)
        return {
            "card": card_to_dict(result["card"]),
            "review_log": review_log_to_dict(result["log"]),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}/status")
def session_status(session_id: str, study_service=Depends(get_study_service), user_id: int = Depends(get_current_user_id)):
    try:
        return {"finished": study_service.is_finished(user_id, session_id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
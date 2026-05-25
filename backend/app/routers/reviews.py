from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_review_service, get_current_user_id
from backend.schemas.review import ReviewLogOut

router = APIRouter()


def log_to_dict(log):
    return {
        "user_id": log.user_id,
        "review_log_id": log.review_log_id,
        "card_id": log.card_id,
        "deck_id": log.deck_id,
        "note_id": log.note_id,
        "rating": log.rating,
        "old_status": log.old_status,
        "new_status": log.new_status,
        "old_due": log.old_due,
        "new_due": log.new_due,
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


@router.get("", response_model=list[ReviewLogOut])
def list_review_logs(
    review_service=Depends(get_review_service),
    user_id: int = Depends(get_current_user_id),
):
    logs = review_service.get_all_review_logs_history(user_id)
    return [log_to_dict(log) for log in logs]


@router.get("/cards/{card_id}", response_model=list[ReviewLogOut])
def get_review_logs(
    card_id: int,
    review_service=Depends(get_review_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        logs = review_service.get_review_logs_history(user_id, card_id)
        return [log_to_dict(log) for log in logs]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
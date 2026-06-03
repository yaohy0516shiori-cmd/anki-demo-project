from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_ai_card_factory_service, get_current_user_id
from backend.schemas.ai_card_factory import (
    AICardDraftConfirmRequest,
    AICardDraftGenerateRequest,
    AICardDraftReviseRequest,
)


router = APIRouter()


def ai_batch_to_dict(result):
    batch = result["batch"]
    items = result["items"]

    return {
        "batch_id": batch.batch_id,
        "user_id": batch.user_id,
        "deck_id": batch.deck_id,
        "source_type": batch.source_type,
        "source_text": batch.source_text,
        "user_prompt": batch.user_prompt,
        "status": batch.status,
        "created_at": batch.created_at,
        "updated_at": batch.updated_at,
        "items": [
            {
                "item_id": row.item.item_id,
                "note_type_id": row.item.note_type_id,
                "status": row.item.status,
                "created_note_id": row.item.created_note_id,
                "error_message": row.item.error_message,
                "latest_version": {
                    "version_id": row.latest_version.version_id,
                    "version_no": row.latest_version.version_no,
                    "fields": row.latest_version.fields,
                    "tags": row.latest_version.tags,
                    "hint": row.latest_version.hint,
                    "reason": row.latest_version.reason,
                    "user_instruction": row.latest_version.user_instruction,
                    "created_by": row.latest_version.created_by,
                    "created_at": row.latest_version.created_at,
                },
            }
            for row in items
        ],
    }


@router.post("/drafts/generate")
def generate_card_drafts(
    payload: AICardDraftGenerateRequest,
    service=Depends(get_ai_card_factory_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        result = service.generate_drafts(
            user_id=user_id,
            source_text=payload.source_text,
            user_prompt=payload.user_prompt,
            deck_id=payload.deck_id,
            note_type_id=payload.note_type_id,
            max_cards=payload.max_cards,
            language=payload.language,
        )
        return ai_batch_to_dict(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/drafts/{batch_id}")
def get_card_draft_batch(
    batch_id: int,
    service=Depends(get_ai_card_factory_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        result = service.get_batch(user_id, batch_id)
        return ai_batch_to_dict(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/drafts/{batch_id}/revise")
def revise_card_drafts(
    batch_id: int,
    payload: AICardDraftReviseRequest,
    service=Depends(get_ai_card_factory_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        result = service.revise_drafts(
            user_id=user_id,
            batch_id=batch_id,
            user_instruction=payload.user_instruction,
            language=payload.language,
        )
        return ai_batch_to_dict(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/drafts/{batch_id}/confirm")
def confirm_card_drafts(
    batch_id: int,
    payload: AICardDraftConfirmRequest,
    service=Depends(get_ai_card_factory_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return service.confirm_drafts(
            user_id=user_id,
            batch_id=batch_id,
            accepted_item_ids=payload.accepted_item_ids,
            rejected_item_ids=payload.rejected_item_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/drafts/{batch_id}")
def discard_card_draft_batch(
    batch_id: int,
    service=Depends(get_ai_card_factory_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return service.discard_batch(user_id, batch_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
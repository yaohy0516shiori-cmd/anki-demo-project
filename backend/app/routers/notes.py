from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_note_service
from backend.schemas.note import NoteCreate, NoteUpdate
from coreengine.note_type.type_registry import get_note_type

router = APIRouter()


def note_to_dict(note):
    return {
        "note_id": note.note_id,
        "note_type_id": note.note_type_id,
        "fields": note.fields,
        "tags": note.tags,
        "hint": note.hint,
        "sort_field": note.sort_field,
        "checksum": note.checksum,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }


@router.post("")
def create_note(payload: NoteCreate, note_service=Depends(get_note_service)):
    try:
        note_type = get_note_type(payload.note_type_id)
        note_id = note_service.create_note(
            note_type=note_type,
            fields=payload.fields,
            tags=payload.tags,
            hint=payload.hint,
            deck_id=payload.deck_id,
        )
        note = note_service.get_note(note_id)
        return note_to_dict(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{note_id}")
def get_note(note_id: int, note_service=Depends(get_note_service)):
    try:
        note = note_service.get_note(note_id)
        return note_to_dict(note)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("")
def list_notes(note_service=Depends(get_note_service)):
    return [note_to_dict(note) for note in note_service.list_notes()]


@router.patch("/{note_id}")
def update_note(note_id: int, payload: NoteUpdate, note_service=Depends(get_note_service)):
    try:
        note_service.update_note(
            note_id=note_id,
            fields=payload.fields,
            tags=payload.tags,
            hint=payload.hint,
        )
        note = note_service.get_note(note_id)
        return note_to_dict(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{note_id}")
def delete_note(note_id: int, note_service=Depends(get_note_service)):
    try:
        result = note_service.delete_note(note_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
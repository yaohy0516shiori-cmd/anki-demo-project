from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_deck_service, get_current_user_id
from backend.schemas.deck import DeckCreate, DeckUpdate
from coreengine.deck.deckmodel import Deck

'''
CREATE ROUTERS HERE: API ENDPOINTS FOR DECKS, HTTP REQUESTS, ETC.
'''

router = APIRouter()


def deck_to_dict(deck):
    return {
        "user_id": deck.user_id,
        "deck_id": deck.deck_id,
        "deck_name": deck.deck_name,
        "deck_description": deck.deck_description,
        "is_default": deck.is_default,
        "created_at": deck.created_at,
        "updated_at": deck.updated_at,
    }


@router.post("")
def create_deck(payload: DeckCreate, deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    try:
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        deck = Deck(
            user_id=user_id,
            deck_name=payload.deck_name,
            deck_description=payload.deck_description,
            created_at=now,
            updated_at=now,
        )
        saved = deck_service.create_deck(deck)
        return deck_to_dict(saved)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
def list_decks(deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    return [deck_to_dict(deck) for deck in deck_service.get_all_decks(user_id)]


@router.get("/{deck_id}")
def get_deck(deck_id: int, deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    try:
        deck = deck_service.get_deck(user_id, deck_id)
        return deck_to_dict(deck)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{deck_id}")
def update_deck(deck_id: int, payload: DeckUpdate, deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    try:
        current = deck_service.get_deck(user_id, deck_id)
        current.deck_name = payload.deck_name if payload.deck_name is not None else current.deck_name
        current.deck_description = (
            payload.deck_description if payload.deck_description is not None else current.deck_description
        )
        current.touch()
        saved = deck_service.update_deck(user_id, current)
        return deck_to_dict(saved)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, hard: bool = False, deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    try:
        if hard:
            return deck_service.delete_deck_and_cards(user_id, deck_id)
        message = deck_service.delete_deck(user_id, deck_id)
        return message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{deck_id}/cards")
def get_deck_cards(deck_id: int, deck_service=Depends(get_deck_service), user_id: int = Depends(get_current_user_id)):
    try:
        cards = deck_service.get_cards_by_deck_id(user_id, deck_id)
        return [card.to_dict() for card in cards]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
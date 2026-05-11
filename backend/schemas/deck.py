from pydantic import BaseModel

# POST, PATCH, GET, DELETE, DATA STRUCTURES FOR DECKS
# POST: CREATE A NEW DECK
# PATCH: UPDATE A DECK
# GET: GET A DECK
# DELETE: DELETE A DECK
# DATA STRUCTURES:
# DeckCreate: CREATE A NEW DECK
# DeckUpdate: UPDATE A DECK
# DeckOut: GET A DECK
# DeckDelete: DELETE A DECK

class DeckCreate(BaseModel):
    deck_name: str
    deck_description: str = ""


class DeckUpdate(BaseModel):
    deck_name: str | None = None
    deck_description: str | None = None


class DeckOut(BaseModel):
    user_id: int
    deck_id: int
    deck_name: str
    deck_description: str
    is_default: bool
    created_at: str
    updated_at: str
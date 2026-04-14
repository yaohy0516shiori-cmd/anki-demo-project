from datetime import datetime, timezone

class Deck:
    def __init__(
        self, 
        deck_id: int, 
        deck_name:str | None=None, 
        deck_description:str | None=None, 
        deck_created_at:str | None=None, 
        deck_updated_at:str | None=None
        ):
        if not isinstance(deck_id, int) or deck_id < 0:
            raise ValueError("Deck id is not an integer or is not positive")
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.deck_id=deck_id
        self.deck_name=deck_name if deck_name is not None else f"Deck {deck_id}"
        self.deck_description=str(deck_description) if deck_description is not None else ""
        self.deck_created_at=deck_created_at if deck_created_at is not None else now
        self.deck_updated_at=deck_updated_at if deck_updated_at is not None else now
    
    def to_dict(self):
        return {
            "deck_id": self.deck_id,
            "deck_name": self.deck_name,
            "deck_description": self.deck_description,
            "deck_created_at": self.deck_created_at,
            "deck_updated_at": self.deck_updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return Deck(
            deck_id=data["deck_id"], 
            deck_name=data["deck_name"], 
            deck_description=data["deck_description"], 
            deck_created_at=data["deck_created_at"], 
            deck_updated_at=data["deck_updated_at"]
            )
        

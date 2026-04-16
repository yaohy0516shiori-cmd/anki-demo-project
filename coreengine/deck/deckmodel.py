from datetime import datetime, timezone

class Deck:
    def __init__(
        self, 
        deck_id: int | None=None, 
        deck_name:str | None=None, 
        deck_description:str | None=None, 
        created_at:str | None=None, 
        updated_at:str | None=None
        ):
        if deck_id is not None:
            if not isinstance(deck_id, int) or deck_id < 0:
                raise ValueError("Deck id is not an integer or is not positive")
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.deck_name=deck_name.strip() if deck_name is not None else f"Deck {deck_id}"
        self.deck_id=deck_id
        self.deck_description=str(deck_description).strip() if deck_description is not None else ""
        self.created_at=created_at.strip() if created_at.strip() is not None else now
        self.updated_at=updated_at.strip() if updated_at.strip() is not None else now
    
    def to_dict(self):
        return {
            "deck_id": self.deck_id,
            "deck_name": self.deck_name,
            "deck_description": self.deck_description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return Deck(
            deck_id=data["deck_id"], 
            deck_name=data["deck_name"], 
            deck_description=data["deck_description"], 
            created_at=data["created_at"], 
            updated_at=data["updated_at"]
            )
    
    def touch(self):
        self.updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        

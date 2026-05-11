from .deckmodel import Deck
from datetime import datetime, timezone

from .deck_repository import DeckRepository
class InmemoryDeckRepository(DeckRepository):
    def __init__(self):
        self.__decks={}
        self.__next_deck_id=1
    
    def __serialize_deck(self,deck:Deck):
        return deck.to_dict()
    
    def __deserialize_deck(self,data):
        return Deck.from_dict(data)
    
    def create_deck(self, deck:Deck):
        if deck.deck_id in self.__decks:
            raise ValueError("Deck already exists")
        if deck.deck_id is not None :
            raise ValueError("New Deck's id should be None")
        if self.__decks[deck.user_id] is None:
            deck.is_default=True
            deck.deck_id=1
            deck.deck_name=f"Default Deck for User {deck.user_id}"
            deck.deck_description=f"Default deck for the user {deck.user_id}"
            deck.created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            deck.updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            self.__decks[deck.user_id][deck.deck_id]=self.__serialize_deck(deck)
        # 不同user id的deck需要重新计数怎么处理？
        else:
            self.__next_deck_id=deck.deck_id
            self.__decks[deck.user_id][deck.deck_id]=self.__serialize_deck(deck)
        self.__next_deck_id+=1
        return self.__deserialize_deck(self.__decks[deck.user_id][deck.deck_id])
    
    def update_deck(self, user_id: int, deck:Deck):
        if deck.deck_id is None:
            raise ValueError("Update Deck's id should not be None")
        if deck.deck_id not in self.__decks[deck.user_id]:
            raise ValueError("Deck not found")
        old=self.__decks[deck.user_id][deck.deck_id]
        update=Deck(
            user_id= deck.user_id,
            deck_id= deck.deck_id,
            deck_name= deck.deck_name,
            deck_description= deck.deck_description,
            updated_at= deck.updated_at,
            created_at= old["created_at"]
            )
        self.__decks[deck.user_id][deck.deck_id]=self.__serialize_deck(update)
        deck.touch()
        return self.__deserialize_deck(self.__decks[deck.user_id][deck.deck_id])
        
    def delete_deck(self, user_id: int, deck_id:int):
        if not self.__decks[user_id][deck_id]:
            raise ValueError("Deck not found")
        if deck_id == 1:
            raise ValueError("Default deck cannot be deleted")
        del self.__decks[user_id][deck_id]
        return 1
    
    def get_all_decks(self, user_id: int):
        return [self.__deserialize_deck(deck) for deck in self.__decks[user_id].values()]
    
    def get_all_decks_ids(self, user_id: int):
        return list(self.__decks[user_id].keys())

    def get_default_deck(self, user_id: int):
        return self.__deserialize_deck(self.__decks[user_id][1])
    
    def get_default_deck_id(self, user_id: int):
        return 1
    
    def is_default_deck(self, user_id: int, deck_id:int):
        if deck_id == 1:
            return True
        return False
    
    def clear_decks(self, user_id: int):
        self.__decks={
            user_id:Deck(user_id=user_id, deck_id=1, deck_name="Default", deck_description="System Default Deck").to_dict()
        }
        self.__next_deck_id=2
    
    def get_deck_by_id(self, user_id: int, deck_id:int):
        if not self.__decks[user_id][deck_id]:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(self.__decks[user_id][deck_id])
    
    def get_deck_by_name(self, user_id: int, deck_name:str):
        for deck in self.__decks[user_id].values():
            if deck["deck_name"] == deck_name:
                return self.__deserialize_deck(deck)
        raise ValueError("Deck not found")

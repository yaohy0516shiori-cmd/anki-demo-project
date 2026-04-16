from .deckmodel import Deck
from datetime import datetime, timezone

class InmemoryDeckRepository:
    def __init__(self):
        self.__decks={
            1:Deck(deck_id=1, deck_name="Default Deck", deck_description="System Default Deck").to_dict()
        }
        self.__next_id=2
    
    def __serialize_deck(self,deck:Deck):
        return deck.to_dict()
    
    def __deserialize_deck(self,data):
        return Deck.from_dict(data)
    
    def create_deck(self, deck:Deck):
        if deck.deck_id in self.__decks:
            raise ValueError("Deck already exists")
        if deck.deck_id is not None :
            raise ValueError("New Deck's id should be None")
        deck.deck_id=self.__next_id
        self.__next_id+=1
        self.__decks[deck.deck_id]=self.__serialize_deck(deck)
        return self.__deserialize_deck(self.__decks[deck.deck_id])
    
    def get_deck(self, deck_id:int):
        if deck_id not in self.__decks:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(self.__decks[deck_id])
    
    def update_deck(self, deck:Deck):
        if deck.deck_id is None:
            raise ValueError("Update Deck's id should not be None")
        if deck.deck_id not in self.__decks:
            raise ValueError("Deck not found")
        old=self.__decks[deck.deck_id]
        update=Deck(
            deck_id= deck.deck_id,
            deck_name= deck.deck_name,
            deck_description= deck.deck_description,
            updated_at= deck.updated_at,
            created_at= old["created_at"]
            )
        self.__decks[deck.deck_id]=self.__serialize_deck(update)
        deck.touch()
        return self.__deserialize_deck(self.__decks[deck.deck_id])
        
    def delete_deck(self, deck_id:int):
        if deck_id not in self.__decks:
            raise ValueError("Deck not found")
        if deck_id == 1:
            raise ValueError("Default deck cannot be deleted")
        del self.__decks[deck_id]
        return deck_id
    
    def get_all_decks(self):
        return [self.__deserialize_deck(deck) for deck in self.__decks.values()]
    
    def get_all_decks_ids(self):
        return list(self.__decks.keys())

    def get_default_deck(self):
        return self.__deserialize_deck(self.__decks[1])
    
    def get_default_deck_id(self):
        return 1
    
    def is_default_deck(self, deck_id:int):
        return deck_id == 1
    
    def clear_decks(self):
        self.__decks={
            1:Deck(deck_id=1, deck_name="Default Deck", deck_description="System Default Deck").to_dict()
        }
        self.__next_id=2
    
    def get_deck_by_id(self, deck_id:int):
        if deck_id not in self.__decks:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(self.__decks[deck_id])
    
    def get_deck_by_name(self, deck_name:str):
        for deck in self.__decks.values():
            if deck["deck_name"] == deck_name:
                return self.__deserialize_deck(deck)
        raise ValueError("Deck not found")
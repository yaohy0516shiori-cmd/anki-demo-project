from .deckmodel import Deck
from datetime import datetime, timezone

class InmemoryDeckRepository:
    def __init__(self):
        self.__decks={
            0:Deck(deck_id=0, deck_name="Default Deck", deck_description="Default Deck").to_dict()
        }
        self.__next_id=1
    
    def __serialize_deck(self,deck):
        return {
            'deck_id': deck.deck_id,
            'deck_name': deck.deck_name,
            'deck_description': deck.deck_description,
            'deck_created_at': deck.deck_created_at,
            'deck_updated_at': deck.deck_updated_at
        }
    
    def __deserialize_deck(self,data):
        return Deck(
            deck_id=data['deck_id'],
            deck_name=data['deck_name'],
            deck_description=data['deck_description'],
            deck_created_at=data['deck_created_at'],
            deck_updated_at=data['deck_updated_at']
        )
    
    def create_deck(self, deck:Deck):
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
        self.__decks[deck.deck_id]=self.__serialize_deck(deck)
        return self.__deserialize_deck(self.__decks[deck.deck_id])
    
    def delete_deck(self, deck_id:int):
        if deck_id not in self.__decks:
            raise ValueError("Deck not found")
        if deck_id == 0:
            raise ValueError("Default deck cannot be deleted")
        del self.__decks[deck_id]
        return deck_id
    
    
    def get_all_decks(self):
        return [self.__deserialize_deck(deck) for deck in self.__decks.values()]
    
    def get_all_decks_ids(self):
        return list(self.__decks.keys())
    
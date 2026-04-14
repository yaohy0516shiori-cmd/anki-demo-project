from .repository import InmemoryDeckRepository
from .deckmodel import Deck

class DeckService:
    def __init__(self, repository_deck:InmemoryDeckRepository):
        self.__repository_deck=repository_deck
    
    def create_deck(self, deck:Deck):
        return self.__repository_deck.create_deck(deck)
    
    def get_deck(self, deck_id:int):
        return self.__repository_deck.get_deck(deck_id)
    
    def update_deck(self, deck:Deck):
        return self.__repository_deck.update_deck(deck)

    def delete_deck(self, deck_id:int):
        return self.__repository_deck.delete_deck(deck_id)
    
    def get_all_decks(self):
        return self.__repository_deck.get_all_decks()
    
    def get_all_decks_ids(self):
        return self.__repository_deck.get_all_decks_ids()
    
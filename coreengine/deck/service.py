from .repository import InmemoryDeckRepository
from .deckmodel import Deck
from ..card.service import CardService
from datetime import date

class DeckService:
    def __init__(self, repository_deck:InmemoryDeckRepository,card_service:CardService):
        self.__repository_deck=repository_deck
        self.__card_service=card_service
    
    def create_deck(self, deck:Deck):
        return self.__repository_deck.create_deck(deck)
    
    def get_deck(self, deck_id:int):
        return self.__repository_deck.get_deck(deck_id)
    
    def update_deck(self, deck:Deck):
        return self.__repository_deck.update_deck(deck)

    def delete_deck(self, deck_id:int):
        deck=self.__repository_deck.get_deck(deck_id)
        
        if self.__repository_deck.is_default_deck(deck_id):
            raise ValueError("Default deck cannot be deleted")

        default_deck=self.__repository_deck.get_default_deck()

        self.__card_service.move_cards_to_deck(deck.deck_id, default_deck.deck_id)
        return self.__repository_deck.delete_deck(deck_id)
    
    def delete_deck_and_cards(self, deck_id:int):
        return self.__repository_deck.delete_deck_and_cards(deck_id)
        
    def get_all_decks(self):
        return self.__repository_deck.get_all_decks()
    
    def get_all_decks_ids(self):
        return self.__repository_deck.get_all_decks_ids()
    
    def get_cards_by_deck_id(self, deck_id:int):
        return self.__card_service.get_cards_by_deck_id(deck_id)
    
    def move_cards_to_deck(self, from_deck_id:int, to_deck_id:int):
        return self.__card_service.move_cards_to_deck(from_deck_id, to_deck_id)
    
    def move_note_cards_to_deck(self, note_id:int, deck_id:int):
        return self.__card_service.move_note_cards_to_deck(note_id, deck_id)
    
    def get_due_cards_by_deck_id(self, deck_id:int, today:date):
        return self.__card_service.get_due_cards_by_deck_id(deck_id, today)
    
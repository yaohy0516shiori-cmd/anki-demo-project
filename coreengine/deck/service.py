from .deckmodel import Deck
from datetime import date
from contextlib import nullcontext

class DeckService:
    def __init__(self, repository_deck,card_service,transaction_manager=None):
        self.__repository_deck=repository_deck
        self.__card_service=card_service
        self.__transaction_manager=transaction_manager
    
    def __transaction(self):
        # used to manage the transaction
        if self.__transaction_manager is None:
            return nullcontext()
        return self.__transaction_manager.transaction()
    
    def create_deck(self, deck:Deck):
        with self.__transaction():
            return self.__repository_deck.create_deck(deck)
    
    def get_deck(self, user_id:int, deck_id:int):
        deck = self.__repository_deck.get_deck(user_id, deck_id)
        if deck is None:
            raise ValueError("Deck not found")
        if deck.user_id != user_id:
            raise ValueError("Deck does not belong to this user")
        return deck
    
    def update_deck(self, user_id:int, deck:Deck):
        with self.__transaction():
            return self.__repository_deck.update_deck(user_id, deck)

    def delete_deck(self, user_id:int, deck_id:int):
        # Safe delete: preserve cards by moving them to default deck
        with self.__transaction():
            deck = self.__repository_deck.get_deck(user_id, deck_id)

            if self.__repository_deck.is_default_deck(user_id, deck_id):
                raise ValueError("Default deck cannot be deleted")

            default_deck = self.__repository_deck.get_default_deck(user_id)

            move_result = self.__card_service.move_cards_to_deck(
                user_id,
                deck.deck_id,
                default_deck.deck_id,
            )

            deleted_deck_count = self.__repository_deck.delete_deck(user_id, deck_id)

        return {
            "message": (
                f"deleted deck {deck_id} and moved "
                f"{move_result['moved_card_count']} cards to default deck"
            ),
            "deleted_deck_id": deck_id,
            "deleted_deck_name": deck.deck_name,
            "deleted_deck_count": deleted_deck_count,
            "moved_card_count": move_result["moved_card_count"],
            "target_deck_id": default_deck.deck_id,
        }
    
    def delete_deck_and_cards(self, user_id:int, deck_id:int):
        # Hard delete: delete deck and all its cards
        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        if self.__repository_deck.is_default_deck(user_id, deck_id):
            raise ValueError("Default deck cannot be deleted")

        with self.__transaction():
            deck = self.__repository_deck.get_deck(user_id, deck_id)
            card_delete_result = self.__card_service.delete_cards_by_deck_id(user_id, deck_id)
            deleted_deck_count = self.__repository_deck.delete_deck(user_id, deck_id)

        return {
            "message": (
                f"deleted deck {deck_id} and "
                f"{card_delete_result['deleted_card_count']} cards"
            ),
            "deleted_deck_id": deck_id,
            "deleted_deck_name": deck.deck_name,
            "deleted_deck_count": deleted_deck_count,
            "deleted_card_count": card_delete_result["deleted_card_count"],
        }
        
    def get_all_decks(self, user_id:int):
        return self.__repository_deck.get_all_decks(user_id)
    
    def get_all_decks_ids(self, user_id:int):
        return self.__repository_deck.get_all_decks_ids(user_id)
    
    def get_cards_by_deck_id(self, user_id:int, deck_id:int):
        self.get_deck(user_id, deck_id)
        return self.__card_service.get_cards_by_deck_id(user_id, deck_id)
    
    def move_cards_to_deck(self, user_id:int, from_deck_id:int, to_deck_id:int):
        with self.__transaction():
            return self.__card_service.move_cards_to_deck(user_id, from_deck_id, to_deck_id)
    
    def move_note_cards_to_deck(self, user_id:int, note_id:int, deck_id:int):
        with self.__transaction():
            return self.__card_service.move_note_cards_to_deck(user_id, note_id, deck_id)

    def get_due_cards_by_deck_id(self, user_id:int, deck_id:int, today:date):
        return self.__card_service.get_due_cards_by_deck_id(user_id, deck_id, today)
    
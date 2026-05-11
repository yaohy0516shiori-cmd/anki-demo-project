from abc import ABC, abstractmethod
from datetime import date
from .cardmodel import Card


class CardRepository(ABC):
    @abstractmethod
    def add_card(self, card: Card) -> Card:
        pass

    @abstractmethod
    def get_card(self, user_id:int, card_id: int) -> Card:
        pass

    @abstractmethod
    def update_card(self, user_id:int, card: Card) -> Card:
        pass

    @abstractmethod
    def delete_card(self, user_id:int, card_id: int) -> None:
        pass

    @abstractmethod
    def get_cards_by_note_id(self, user_id:int, note_id: int) -> list[Card]:
        pass

    @abstractmethod
    def get_cards_by_note_id_and_ord(self, user_id:int, note_id: int, template_ord: int) -> Card | None:
        pass

    @abstractmethod
    def get_cards_by_deck_id(self, user_id:int, deck_id: int) -> list[Card]:
        pass

    @abstractmethod
    def get_due_cards_by_deck_id(self, user_id:int, deck_id: int, today: date) -> list[Card]:
        pass

    @abstractmethod
    def list_cards(self, user_id:int) -> list[Card]:
        pass

    @abstractmethod
    def delete_cards_by_note_id(self, user_id:int, note_id: int) -> int:
        pass

    @abstractmethod
    def delete_cards_by_note_id_and_ord(self, user_id:int, note_id: int, template_ord: int) -> int:
        pass

    @abstractmethod
    def delete_cards_by_deck_id(self, user_id:int, deck_id: int) -> int:
        pass

    @abstractmethod
    def move_cards_to_deck(self, user_id:int, from_deck_id: int, to_deck_id: int) -> int:
        pass

    @abstractmethod
    def move_note_cards_to_deck(self, user_id:int, note_id: int, deck_id: int) -> int:
        pass

    @abstractmethod
    def count_cards(self, user_id:int) -> int:
        pass
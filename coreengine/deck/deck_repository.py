from abc import ABC, abstractmethod

from .deckmodel import Deck


class DeckRepository(ABC):
    @abstractmethod
    def create_deck(self, deck: Deck) -> Deck:
        pass

    @abstractmethod
    def get_deck(self, user_id: int, deck_id: int) -> Deck:
        pass

    @abstractmethod
    def update_deck(self, user_id: int, deck: Deck) -> Deck:
        pass

    @abstractmethod
    def delete_deck(self, user_id: int, deck_id: int) -> None:
        pass

    @abstractmethod
    def get_all_decks(self, user_id: int) -> list[Deck]:
        pass

    @abstractmethod
    def get_all_decks_ids(self, user_id: int) -> list[int]:
        pass

    @abstractmethod
    def get_default_deck(self, user_id: int) -> Deck:
        pass

    @abstractmethod
    def get_default_deck_id(self, user_id: int) -> int:
        pass

    @abstractmethod
    def is_default_deck(self, user_id: int, deck_id: int) -> bool:
        pass

    @abstractmethod
    def clear_decks(self, user_id: int) -> None:
        pass

    @abstractmethod
    def get_deck_by_name(self, user_id: int, deck_name: str) -> Deck:
        pass
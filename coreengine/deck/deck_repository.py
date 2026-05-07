from abc import ABC, abstractmethod

from .deckmodel import Deck


class DeckRepository(ABC):
    @abstractmethod
    def create_deck(self, deck: Deck) -> Deck:
        pass

    @abstractmethod
    def get_deck(self, deck_id: int) -> Deck:
        pass

    @abstractmethod
    def update_deck(self, deck: Deck) -> Deck:
        pass

    @abstractmethod
    def delete_deck(self, deck_id: int) -> None:
        pass

    @abstractmethod
    def get_all_decks(self) -> list[Deck]:
        pass

    @abstractmethod
    def get_all_decks_ids(self) -> list[int]:
        pass

    @abstractmethod
    def get_default_deck(self) -> Deck:
        pass

    @abstractmethod
    def get_default_deck_id(self) -> int:
        pass

    @abstractmethod
    def is_default_deck(self, deck_id: int) -> bool:
        pass

    @abstractmethod
    def clear_decks(self) -> None:
        pass

    @abstractmethod
    def get_deck_by_name(self, deck_name: str) -> Deck:
        pass
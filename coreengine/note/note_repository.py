from abc import ABC, abstractmethod

from .notemodels import Note


class NoteRepository(ABC):
    @abstractmethod
    def add_note(self, note: Note) -> int:
        pass

    @abstractmethod
    def get_note(self, note_id: int) -> Note:
        pass

    @abstractmethod
    def update_note(self, note: Note) -> int:
        pass

    @abstractmethod
    def delete_note(self, note_id: int) -> None:
        pass

    @abstractmethod
    def get_all_notes(self) -> list[Note]:
        pass

    @abstractmethod
    def clear_cards(self) -> int:
        pass
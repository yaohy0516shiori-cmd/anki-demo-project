from abc import ABC, abstractmethod

from .notemodels import Note


class NoteRepository(ABC):
    @abstractmethod
    def add_note(self, user_id:int, note: Note) -> Note:
        pass

    @abstractmethod
    def get_note(self, user_id:int, note_id: int) -> Note:
        pass

    @abstractmethod
    def update_note(self, user_id:int, note: Note) -> Note:
        pass

    @abstractmethod
    def delete_note(self, user_id:int, note_id: int) -> None:
        pass

    @abstractmethod
    def get_all_notes(self, user_id:int) -> list[Note]:
        pass
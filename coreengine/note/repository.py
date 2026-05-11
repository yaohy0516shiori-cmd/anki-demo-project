# In-memory repository: simulate SQLite
from .notemodels import Note
from datetime import datetime, timezone
from .note_repository import NoteRepository
class InMemoryNoteRepository(NoteRepository):
    def __init__(self):
        self.__notes={}
        self.__next_id=1

    def __serialize_note(self,note:Note):
        # serialize the note to a dictionary
        return {
            "note_id": note.note_id,
            "user_id": note.user_id,
            "note_type_id": note.note_type_id,
            "fields": note.fields,
            "tags": note.tags,
            "sort_field": note.sort_field,
            "checksum": note.checksum,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "hint": note.hint if note.hint is not None else ''
        }
    
    def __deserialize_note(self,data:dict):
        # deserialize the note from a dictionary
        return Note(
            user_id=data["user_id"],
            note_type_id=data["note_type_id"],
            fields=data["fields"],
            note_id=data["note_id"],
            tags=data["tags"],
            sort_field=data["sort_field"],
            checksum=data["checksum"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            hint=data["hint"] if data["hint"] is not None else '')
    
    def add_note(self,note:Note):
        # add a note to the repository and assign a new id to the note
        # lose a part to judge whether the note is legal?
        if note.note_id is not None:
            raise ValueError("New Note's id should be None")
        if note.user_id not in self.__notes:
            self.__notes[note.user_id]={}
            note.note_id=1
        elif self.__notes[note.user_id][note.note_id] is not None:
            note.note_id+=1
            self.__next_id=note.note_id
        self.__next_id+=1
        serialized_note=self.__serialize_note(note)
        self.__notes[note.user_id][note.note_id]=serialized_note
        return self.__deserialize_note(self.__notes[note.user_id][note.note_id])
    
    def get_note(self,user_id:int, note_id:int):
        # get a note from the repository by id
        if not isinstance(user_id,int) or not isinstance(note_id,int):
            raise TypeError("User id and note id must be integers")
        elif user_id not in self.__notes:
            raise ValueError("User not found")
        elif note_id not in self.__notes[user_id]:
            raise ValueError("Note not found")
        return self.__deserialize_note(self.__notes[user_id][note_id])
    
    def update_note(self,user_id:int, note:Note):
        # update a note in the repository
        # lose a part to judge whether the note is legal
        if not isinstance(user_id,int) or not isinstance(note.note_id,int):
            raise TypeError("User id and note id must be integers")
        elif user_id not in self.__notes:
            raise ValueError("User not found")
        elif note.note_id not in self.__notes[user_id]:
            raise ValueError("Note not found")
        serialized_note=self.__serialize_note(note)
        self.__notes[user_id][note.note_id]=serialized_note
        return self.__deserialize_note(self.__notes[user_id][note.note_id])
    
    def delete_note(self,user_id:int, note_id:int):
        # delete a note from the repository
        if not isinstance(user_id,int) or not isinstance(note_id,int):
            raise TypeError("User id and note id must be integers")
        elif user_id not in self.__notes:
            raise ValueError("User not found")
        elif note_id not in self.__notes[user_id]:
            raise ValueError("Note not found")
        del self.__notes[user_id][note_id]
        return 1
    
    def get_all_notes(self, user_id:int):
        # get all notes from the repository
        if not isinstance(user_id,int):
            raise TypeError("User id must be an integer")
        elif user_id not in self.__notes:
            raise ValueError("User not found")
        return [self.__deserialize_note(note) for note in self.__notes[user_id].values()]
    
# In-memory repository: simulate SQLite
from note.notemodels import Note
from datetime import datetime, timezone
class InMemoryNoteRepository:
    def __init__(self):
        self.__notes={}
        self.__next_id=1
    def __serialize_note(self,note:Note):
        return {
            "id": note.note_id,
            "note_type_id": note.note_type_id,
            "fields": note.fields,
            "tags": note.tags,
            "sort_field": note.sort_field,
            "checksum": note.checksum,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
    
    def __deserialize_note(self,data:dict):
        return Note(
            note_type_id=data["note_type_id"],
            fields=data["fields"],
            note_id=data["id"],
            tags=data["tags"],
            sort_field=data["sort_field"],
            checksum=data["checksum"],
            created_at=data["created_at"],
            updated_at=data["updated_at"])
    
    def add_note(self,note:Note):
        # lose a part to judge whether the note is legal?
        if note.note_id is not None:
            raise ValueError("New Note's id should be None")
        # what about the other part? how to judge whether the note is legal?
        note.note_id=self.__next_id
        self.__next_id+=1
        serialized_note=self.__serialize_note(note)
        # but under the system it should be stored like a instance of the Note class? what is it in the sqlite?
        self.__notes[note.note_id]=serialized_note
        # or return nothing?
        return note.note_id
    
    def get_note(self,note_id:int):
        if not isinstance(note_id,int):
            raise TypeError("Note id is not an integer")
        elif note_id not in self.__notes:
            raise ValueError("Note not found")
        # it offer a instance for other module to deal with
        return self.__deserialize_note(self.__notes[note_id])
    
    def update_note(self,note:Note):
        # lose a part to judge whether the note is legal
        if not isinstance(note.note_id,int):
            raise TypeError("Note id is not an integer")
        elif note.note_id not in self.__notes:
            raise ValueError("Note not found")
        serialized_note=self.__serialize_note(note)
        self.__notes[note.note_id]=serialized_note
        return note.note_id
    
    def delete_note(self,note_id:int):
        if not isinstance(note_id,int):
            raise TypeError("Note id is not an integer")
        elif note_id not in self.__notes:
            raise ValueError("Note not found")
        del self.__notes[note_id]
        return "Note deleted successfully"
    
    def get_all_notes(self):
        return [self.__deserialize_note(data) for data in self.__notes.values()]
    
# In-memory repository: simulate SQLite
from note.notemodels import Note
class InMemoryRepository:
    def __init__(self):
        self.__notes={}
        self.__next_id=1
    def __serialize_note(self,note:Note):
        return {
            "id": note.note_id,
            "note_type_id": note.note_type_id,
            "fields": note.field_content,
            "tags": note.user_tags,
            "sort_field": note.sort_field,
            "checksum": note.checksum_hash,
            "created_at": note.created_time,
            "updated_at": note.updated_time
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
        serialized_note=self.__serialize_note(note)
        self.__notes[serialized_note["id"]]=serialized_note
        return note.note_id
    def get_note(self,note_id:int):
        serialized_note=self.__notes[note_id]
        return self.__deserialize_note(serialized_note)
    
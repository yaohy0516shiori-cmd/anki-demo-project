'''
Organize the business process of the note, perform business verification
Not responsible for storage, storage is handed over to the repo.
Not responsible for the consistency of underlying objects, that part is entrusted to Note
'''
from note.notemodels import Note
from note.utils import calculate_checksum
from note.repository import InMemoryRepository_note
from note_type.notetype import NoteType
from note_type.type_registry import get_note_type

class NoteService:
    def __init__(self, repository_note:InMemoryRepository_note):
        self.__repository_note = repository_note

    def create_note(self, note_type, fields, tags=None,note_id=None):
        tags=tags if tags is not None else []
        self.__validate_fields(note_type, fields)
        if self.is_duplicate(fields,note_type.note_type_id,note_id):
            raise ValueError("The note is duplicate")
        note=Note(note_type_id=note_type.note_type_id, fields=fields, tags=tags)
        return self.__repository_note.add_note(note)


    def get_note(self, note_id):
        return self.__repository_note.get_note(note_id)

    def list_notes(self):
        return self.__repository_note.get_all_notes()

    def update_note(self, note_id, fields=None, tags=None):
        note = self.__repository_note.get_note(note_id)
        note_type=get_note_type(note.note_type_id)
        new_fields=note.fields if fields is None else fields
        new_tags=note.tags if tags is None else tags
        self.__validate_fields(note_type, new_fields)
        if self.is_duplicate(new_fields,note.note_type_id,note_id):
            raise ValueError("The note is duplicate")
        note.fields=new_fields
        note.tags=new_tags
        note.refresh()
        return self.__repository_note.update_note(note)

    def delete_note(self, note_id):
        return self.__repository_note.delete_note(note_id)

    def is_duplicate(self, fields, note_type_id, exclude_note_id=None):
        tempchecksum=calculate_checksum(fields)
        notes=self.__repository_note.get_all_notes()
        for note in notes:
            if note.note_id==exclude_note_id and exclude_note_id is not None:
                continue
            if note.checksum==tempchecksum and note.note_type_id==note_type_id:
                return True
        return False

    def __validate_fields(self, note_type:NoteType, fields):
        if len(fields) != len(note_type.field_names):   
            raise ValueError("The number of fields is not equal to the number of field names")
        if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
            raise ValueError("Fields must be a list of strings")
        return True
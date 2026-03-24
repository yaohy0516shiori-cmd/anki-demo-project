'''
Organize the business process of the note, perform business verification
Not responsible for storage, storage is handed over to the repo.
Not responsible for the consistency of underlying objects, that part is entrusted to Note
'''
from note.notemodels import Note
from note.utils import calculate_checksum
from note.repository import InMemoryRepository_note

class NoteService:
    def __init__(self, repository_note:InMemoryRepository_note):
        self._repository_note = repository_note

    def create_note(self, note_type, fields, tags=None,note_id=None):
        self.__validate_fields(note_type, fields)
        if self.is_duplicate(fields,note_id):
            raise ValueError("The note is duplicate")
        note=Note(note_type_id=note_type.note_type_id, fields=fields, tags=tags)
        return self._repository_note.add_note(note)


    def get_note(self, note_id):
        return self._repository_note.get_note(note_id)

    def list_notes(self):
        return self._repository_note.get_all_notes()

    def update_note(self, note_id, fields=None, tags=None):
        note = self._repository_note.get_note(note_id)
        if self.is_duplicate(note.fields,note_id):
            raise ValueError("The note is duplicate")
        if fields is not None:
            # self.__validate_fields(note.note_type(这里note_type id 和 field_names怎么引入？三个模块结合), fields)
            if len(fields) != len(note.fields):
                raise ValueError("The number of fields is not equal to the number of field names")
            else:
                note.fields=fields
        if tags is not None:
            note.tags=tags
        return self._repository_note.update_note(note)

    def delete_note(self, note_id):
        return self._repository_note.delete_note(note_id)

    def is_duplicate(self, fields, exclude_note_id=None):
        tempchecksum=calculate_checksum(fields)
        notes=self._repository_note .get_all_notes()
        for note in notes:
            if note.note_id==exclude_note_id and exclude_note_id is not None:
                continue
            if note.checksum==tempchecksum:
                return True
        return False

    def __validate_fields(self, note_type, fields):
        if len(fields) != len(note_type.field_names):   
            raise ValueError("The number of fields is not equal to the number of field names")
        else:
            return True
'''
Organize the business process of the note, perform business verification
Not responsible for storage, storage is handed over to the repo.
Not responsible for the consistency of underlying objects, that part is entrusted to Note
'''
from .notemodels import Note
from .utils import calculate_checksum
from ..note_type.notetype import NoteType
from ..note_type.type_registry import get_note_type
from contextlib import nullcontext


class NoteService:
    def __init__(self, repository_note, card_service,transaction_manager=None):
        if repository_note is None:
            raise ValueError("Repository note is not set")
        if card_service is None:
            raise ValueError("Card service is not set")
        self.__repository_note = repository_note
        self.__card_service = card_service
        self.__transaction_manager = transaction_manager

    def __transaction(self):
        # used to manage the transaction
        if self.__transaction_manager is None:
            return nullcontext()
        return self.__transaction_manager.transaction()

    def create_note(self, user_id:int, note_type, fields, tags=None, hint=None, deck_id=None, today=None):
        # create a note: validate, deduplicate, construct Note, save to repo
        # deck_id is 0 by default, if deck_id is not set, the note will be created in the default deck
        hint=hint if hint is not None else ''
        tags=tags if tags is not None else []
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User id must be a positive integer")
        if not isinstance(deck_id, int) or deck_id <= 0 or deck_id is None:
            raise ValueError("Deck id must be a positive integer")

        self.__validate_fields(user_id, note_type, fields)
        if self.is_duplicate(user_id, fields,note_type.note_type_id):
            raise ValueError("The note is duplicate")

        with self.__transaction():
            note = Note(
                user_id=user_id,
                note_type_id=note_type.note_type_id,
                fields=fields,
                tags=tags,
                hint=hint,
            )

            saved_note_id = self.__repository_note.add_note(user_id, note)

            saved_note = self.__repository_note.get_note(user_id, saved_note_id)

            self.__card_service.create_cards_from_note(user_id, saved_note,deck_id=deck_id,today=today)

        return saved_note_id


    def get_note(self, user_id:int, note_id:int):
        # get a note from the repository by id
        return self.__repository_note.get_note(user_id, note_id)

    def list_notes(self, user_id:int):
        # get all notes from the repository
        return self.__repository_note.get_all_notes(user_id)

    def update_note(self, user_id:int, note_id:int, fields=None, tags=None,hint=None, today=None):
        # update a note in the repository, fields/tags, refresh, then save to repo
        note = self.__repository_note.get_note(user_id, note_id)
        note_type=get_note_type(note.note_type_id)
        new_fields=note.fields if fields is None else fields
        new_tags=note.tags if tags is None else tags
        new_hint=note.hint if hint is None else hint
        if new_hint is None:
            new_hint = ""
        elif not isinstance(new_hint, str):
            raise ValueError("Hint must be a string")

        self.__validate_fields(user_id, note_type, new_fields)
        if self.is_duplicate(user_id, new_fields,note.note_type_id,note_id):
            raise ValueError("The note is duplicate")
        old_fields=note.fields
        note.fields=new_fields
        note.tags=new_tags
        note.hint=new_hint
        note.refresh()
        with self.__transaction():
            updated_note = self.__repository_note.update_note(user_id, note)

            # it means the note is a cloze note and the fields have changed, so we need to reconcile the cards
            if old_fields!=new_fields:
                self.__card_service.reconcile_cards_for_note(user_id, updated_note, today=today)

        return updated_note.note_id

    def delete_note(self, user_id:int, note_id:int):
        # delete a note from the repository
        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note id must be a positive integer")

        with self.__transaction():
            card_delete_result = self.__card_service.delete_cards_by_note_id(user_id, note_id)
            deleted_card_count = card_delete_result["deleted_card_count"]
            deleted_note_count = self.__repository_note.delete_note(user_id, note_id)
            


        return {
            "message": f"deleted {deleted_note_count} note and {deleted_card_count} cards for note {note_id}",
            "note_id": note_id,
            "deleted_note_count": deleted_note_count,
            "deleted_card_count": deleted_card_count,
        }
        
    def is_duplicate(self, user_id:int, fields, note_type_id, exclude_note_id=None):
        # check if the note is duplicate
        tempchecksum=calculate_checksum(fields)
        notes=self.__repository_note.get_all_notes(user_id)
        for note in notes:
            if note.note_id==exclude_note_id and exclude_note_id is not None:
                continue
            if note.checksum==tempchecksum and note.note_type_id==note_type_id:
                return True
        return False

    def __validate_fields(self, user_id:int, note_type:NoteType, fields):
        # validate the fields of the note
        if len(fields) != len(note_type.field_names):   
            raise ValueError("The number of fields is not equal to the number of field names")
        if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
            raise ValueError("Fields must be a list of strings")
        return True
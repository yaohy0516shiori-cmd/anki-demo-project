# test the note service
from note_type.notetype import NoteType
from note.repository import InMemoryRepository
from note.service import NoteService
from note.notemodels import Note


def build_service():
    note_type = NoteType(
        note_type_id=1,
        name="Basic",
        field_names=["Front", "Back"],
        kind="basic"
    )
    repo = InMemoryRepository()
    service = NoteService(repo)
    return note_type, repo, service


def test_create_note():
    note_type, repo, service = build_service()
    note_id = service.create_note(note_type, ["hello", "你好"], ["english"])
    note = service.get_note(note_id)

    print("test_create_note")
    print(note.note_id == 1)
    print(note.fields == ["hello", "你好"])
    print(note.tags == ["english"])
    print()


def test_duplicate_note():
    note_type, repo, service = build_service()
    service.create_note(note_type, ["hello", "你好"], ["english"])

    print("test_duplicate_note")
    try:
        service.create_note(note_type, ["hello", "四小月"], ["english"])
        print(False)
    except ValueError:
        print(True)
    print()


def test_update_note():
    note_type, repo, service = build_service()
    note_id = service.create_note(note_type, ["hello", "你好"], ["english"])
    service.update_note(note_id, fields=["hi", "你好"], tags=["vocab"])
    note = service.get_note(note_id)

    print("test_update_note")
    print(note.fields == ["hi", "你好"])
    print(note.tags == ["vocab"])
    print()


def main():
    test_create_note()
    test_duplicate_note()
    test_update_note()


if __name__ == "__main__":
    main()
from note_type.notetype import NoteType

BASIC = NoteType(
    note_type_id=1,
    name="Basic",
    field_names=["Front", "Back"],
    kind="basic"
)

BASIC_REVERSE = NoteType(
    note_type_id=2,
    name="BasicReverse",
    field_names=["Front", "Back"],
    kind="basic_reverse"
)

CLOZE = NoteType(
    note_type_id=3,
    name="Cloze",
    field_names=["Text","Back extra"],
    kind="cloze"
)

NOTE_TYPE_REGISTRY = {
    1: BASIC,
    2: BASIC_REVERSE,
    3: CLOZE,
}

def get_note_type(note_type_id: int) -> NoteType:
    note_type = NOTE_TYPE_REGISTRY.get(note_type_id)
    if note_type is None:
        raise ValueError("note type does not exist")
    return note_type
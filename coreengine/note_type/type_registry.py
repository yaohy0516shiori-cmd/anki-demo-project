from .notetype import NoteType

# define basic note type
BASIC = NoteType(
    note_type_id=1,
    name="Basic",
    field_names=["Front", "Back"],
    kind="basic"
)

# define basic reverse note type
BASIC_REVERSE = NoteType(
    note_type_id=2,
    name="BasicReverse",
    field_names=["Front", "Back"],
    kind="basic_reverse"
)

# define cloze note type
CLOZE = NoteType(
    note_type_id=3,
    name="Cloze",
    field_names=["Text","Back extra"],
    kind="cloze"
)

# define note type registry
NOTE_TYPE_REGISTRY = {
    1: BASIC,
    2: BASIC_REVERSE,
    3: CLOZE,
}

# get note type from note type id
def get_note_type(note_type_id: int) -> NoteType:
    note_type = NOTE_TYPE_REGISTRY.get(note_type_id)
    if note_type is None:
        raise ValueError("note type does not exist")
    return note_type
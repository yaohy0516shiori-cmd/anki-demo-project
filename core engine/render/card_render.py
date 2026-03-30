import re
from card.cardmodel import Card
from note.notemodels import Note
from note_type.type_registry import get_note_type

'''
lack of kind: one cloze note generate one card with multiple cloze
question: how to use ai-agent to help user to split a long text into multiple cloze?
'''
# Regex for cloze syntax like:
# {{c1::answer}}
# {{c2::answer::hint}}
#
# Group 1 -> cloze number, e.g. "1"
# Group 2 -> answer text, e.g. "Paris"
# Group 3 -> optional hint, e.g. "city"
CLOZE_PATTERN = re.compile(r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}")


def render_card(card: Card, note: Note) -> dict:
    """
    Render one real study card from one note.

    Why do we need both card and note?
    - note stores the source content
    - card tells us WHICH card generated from that note we are rendering

    Example:
    - a basic note usually generates 1 card
    - a basic_reverse note generates 2 cards
    - a cloze note may generate multiple cards

    So note alone is not enough. We also need card.template_ord
    to know which specific card to render.
    """

    # A saved card should point to a saved note.
    # If note.note_id is None, this note is not a valid persisted note.
    if note.note_id is None:
        raise ValueError("Note id is required")

    # Safety check:
    # the card must belong to this exact note.
    if card.note_id != note.note_id:
        raise ValueError("Card and note ids do not match")

    # Look up the NoteType definition by note.note_type_id.
    # We need NoteType to know how this note should be rendered.
    note_type = get_note_type(note.note_type_id)

    # Use note_type.kind, because "kind" describes behavior:
    # basic / basic_reverse / cloze
    if note_type.kind == "cloze":
        # Why use template_ord here?
        # Because one cloze note may produce multiple cards:
        # c1 -> one card, c2 -> another card, etc.
        # template_ord tells us which cloze card this Card object represents.
        return __render_cloze_card(note, card.template_ord)

    if note_type.kind == "basic":
        # Why does basic not use template_ord?
        # Because a normal basic note only has one rendering pattern:
        # fields[0] -> front, fields[1] -> back
        # There is no "which version" question here.
        return __render_basic_card(note)

    if note_type.kind == "basic_reverse":
        # Why use template_ord here?
        # Because one basic_reverse note creates 2 cards:
        # template 0: front=field0, back=field1
        # template 1: front=field1, back=field0
        return __render_basic_reverse_card(note, card.template_ord)

    raise ValueError(f"Unsupported note type: {note_type.kind}")


def __render_basic_card(note: Note) -> dict:
    """
    Render a normal basic card.
    fields[0] = front content
    fields[1] = back content
    """
    return {
        "front": note.fields[0],
        "back": note.fields[1]
    }


def __render_basic_reverse_card(note: Note, template_ord: int) -> dict:
    """
    Render a reversed basic card.
    template_ord decides which side goes first:
    - 0 -> normal direction
    - 1 -> reversed direction
    """

    # Card version 0:
    # field 0 on front, field 1 on back
    if template_ord == 0:
        return {
            "front": note.fields[0],
            "back": note.fields[1]
        }

    # Card version 1:
    # field 1 on front, field 0 on back
    if template_ord == 1:
        return {
            "front": note.fields[1],
            "back": note.fields[0]
        }

    # Anything else is invalid for basic_reverse.
    raise ValueError(f"Invalid template ord: {template_ord}")


def __render_cloze_card(note: Note, template_ord: int) -> dict:
    """
    Render one cloze card from a cloze note.
    note.fields[0] = main cloze text
    note.fields[1] = optional back extra
    """

    # Main cloze source text is always the first field.
    text = note.fields[0]

    # Second field is optional extra explanation shown on back.
    # If the note does not have a second field, use empty string.
    back_extra = note.fields[1] if len(note.fields) > 1 else ""

    # Why template_ord + 1?
    # Internal card.template_ord is usually 0-based:
    # But cloze syntax is 1-based:
    #   template_ord 0 -> target cloze c1
    #   template_ord 1 -> target cloze c2
    target_ord = template_ord + 1

    # hide_target=True means:
    # on the FRONT side, we hide the target cloze answer
    # and replace it with [____] or [hint].
    front = __replace_cloze(text, target_ord, hide_target=True)

    # hide_target=False means:
    # on the BACK side, we reveal the actual answer.
    back = __replace_cloze(text, target_ord, hide_target=False)

    # back_extra is only appended to the BACK, not the front.
    # This is where extra explanation / notes are shown.
    if back_extra.strip():
        back = f"{back}\n\n{back_extra}"

    return {
        "front": front,
        "back": back
    }


def __replace_cloze(text: str, target_ord: int, hide_target: bool) -> str:
    """
    Replace cloze markup inside the text.

    target_ord = which cloze we are rendering now
    hide_target:
    - True  -> hide the target answer (front side)
    - False -> reveal the target answer (back side)

    Other clozes are kept visible as plain answers.
    """

    # This flag records whether we actually found the target cloze.
    # Example: if target_ord=2 but the text only contains c1, then this stays False.
    found_target = False

    def replacer(match):
        """
        This nested function is called once for each regex match.

        match is a regex Match object for one cloze pattern.
        Example match text: {{c2::Paris::city}}
        """

        # Why use nonlocal?
        # Because found_target is defined in the outer function,
        # and we want to MODIFY that outer variable here.
        nonlocal found_target

        # What is group()?
        # group(1), group(2), group(3) are captured parts from the regex.
        #
        # For {{c2::Paris::city}}:
        # group(1) -> "2"
        # group(2) -> "Paris"
        # group(3) -> "city"
        ord_value = int(match.group(1))
        answer = match.group(2)
        hint = match.group(3)

        # If this is the cloze we are currently rendering:
        if ord_value == target_ord:
            found_target = True

            if hide_target:
                # On front side, hide the answer.
                # If there is a hint, show the hint in brackets.
                # Example: [city]
                # Otherwise use a blank placeholder.
                return f"[{hint}]" if hint else "[____]"

            # On back side, reveal the actual answer.
            return answer

        # For all NON-target clozes:
        # just show their answers normally.
        return answer

    # Why use sub()?
    # re.sub() replaces every regex match in text.
    # Here, every cloze pattern found in the text will be passed to replacer(),
    # and replacer() decides what that match becomes.
    rendered = CLOZE_PATTERN.sub(replacer, text)

    # If we never found the target cloze, the card/template mapping is wrong.
    if not found_target:
        raise ValueError(f"Target cloze ordinal {target_ord} not found in text")

    return rendered
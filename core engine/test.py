from note.repository import InMemoryNoteRepository
from note.service import NoteService
from note_type.type_registry import BASIC, CLOZE
from card.repository import InMemoryCardRepository
from card.service import CardService


def build_services():
    note_repo = InMemoryNoteRepository()
    card_repo = InMemoryCardRepository()
    card_service = CardService(card_repo)
    note_service = NoteService(note_repo, card_service=card_service)
    return note_service, card_service, note_repo, card_repo


def test_basic_create_generates_cards():
    note_service, card_service, note_repo, card_repo = build_services()
    note_id = note_service.create_note(BASIC, ["hello", "你好"], ["english"])
    cards = card_service.get_card_by_note_id(note_id)

    print("test_basic_create_generates_cards")
    print(len(cards) == 1)
    print(cards[0].template_ord == 0)
    print()


def test_cloze_update_reconciles_cards():
    note_service, card_service, note_repo, card_repo = build_services()
    note_id = note_service.create_note(CLOZE, ["{{c1::Paris}} and {{c2::London}}", "extra"], [])
    note_service.update_note(note_id, fields=["{{c1::Paris}} only", "extra"])
    cards = card_service.get_card_by_note_id(note_id)

    print("test_cloze_update_reconciles_cards")
    print(len(cards) == 1)
    print(cards[0].template_ord == 0)
    print()


def test_delete_note_cascades_cards():
    note_service, card_service, note_repo, card_repo = build_services()
    note_id = note_service.create_note(BASIC, ["hello", "你好"], [])
    note_service.delete_note(note_id)
    cards = card_service.get_card_by_note_id(note_id)

    print("test_delete_note_cascades_cards")
    print(len(cards) == 0)
    print()


def main():
    test_basic_create_generates_cards()
    test_cloze_update_reconciles_cards()
    test_delete_note_cascades_cards()


if __name__ == "__main__":
    main()
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from coreengine.note.notemodels import Note
from coreengine.note.note_repository import NoteRepository
from coreengine.storage.sqlalchemy_models import NoteORM,utc_now

class SqlAlchemyNoteRepository(NoteRepository):
    def __init__(self, db: DbSession):
        self.__db = db
    
    def __to_domain(self, orm: NoteORM) -> Note:
        return Note(
            note_id=orm.note_id,
            user_id=orm.user_id,
            note_type_id=orm.note_type_id,
            fields=list(orm.fields_json or []),
            tags=list(orm.tags_json or []),
            sort_field=orm.sort_field,
            checksum=orm.checksum,
            hint=orm.hint or "",
            created_at=orm.created_at.isoformat() if orm.created_at else utc_now().isoformat(),
            updated_at=orm.updated_at.isoformat() if orm.updated_at else utc_now().isoformat(),
        )

    def add_note(self, user_id: int, note: Note) -> int:
        if note.user_id != user_id:
            raise ValueError("User ID does not match")
        if note.note_id is not None:
            raise ValueError("Note ID must be None")

        orm = NoteORM(
            user_id=user_id,
            note_type_id=note.note_type_id,
            fields_json=note.fields,
            tags_json=note.tags,
            sort_field=note.sort_field,
            checksum=note.checksum,
            hint=note.hint or "",
        )

        try:
            self.__db.add(orm)
            self.__db.flush()
        except IntegrityError as exc:
            raise ValueError("Duplicate note") from exc

        return orm.note_id

    def get_note(self, user_id: int, note_id: int) -> Note:
        stmt = select(NoteORM).where(
            NoteORM.user_id == user_id,
            NoteORM.note_id == note_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Note not found")
        return self.__to_domain(orm)

    def update_note(self, user_id: int, note: Note) -> Note:
        stmt = select(NoteORM).where(
            NoteORM.user_id == user_id,
            NoteORM.note_id == note.note_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Note not found")

        orm.note_type_id = note.note_type_id
        orm.fields_json = note.fields
        orm.tags_json = note.tags
        orm.sort_field = note.sort_field
        orm.checksum = note.checksum
        orm.hint = note.hint or ""

        self.__db.flush()
        return self.get_note(user_id, note.note_id)

    def delete_note(self, user_id: int, note_id: int) -> int:
        stmt = select(NoteORM).where(
            NoteORM.user_id == user_id,
            NoteORM.note_id == note_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Note not found")

        self.__db.delete(orm)
        self.__db.flush()

        return 1

    def get_all_notes(self, user_id: int) -> list[Note]:
        stmt = (
            select(NoteORM)
            .where(NoteORM.user_id == user_id)
            .order_by(NoteORM.note_id)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    
import json
import sqlite3
from datetime import datetime,date

from ..note.notemodels import Note
from ..note.note_repository import NoteRepository
class SqliteNoteRepository(NoteRepository):
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_note(self,note:Note)->dict:
        return {
            # note_id is auto incremented
            'user_id':note.user_id,
            'note_type_id':note.note_type_id,
            'fields_JSON':json.dumps(note.fields,ensure_ascii=False),
            'tags_JSON':json.dumps(note.tags,ensure_ascii=False),
            'sort_field':note.sort_field,
            'checksum':note.checksum,
            'created_at':note.created_at,
            'updated_at':note.updated_at,
            'hint':note.hint if note.hint is not None else '',
        }
    
    def __deserialize_note(self,row:sqlite3.Row)->Note:
        return Note(
            note_id=row['note_id'],
            user_id=row['user_id'],
            note_type_id=row['note_type_id'],
            fields=json.loads(row['fields_JSON']),
            tags=json.loads(row['tags_JSON']),
            sort_field=row['sort_field'],
            checksum=row['checksum'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            hint=row['hint'] if row['hint'] is not None else '',
        )
    
    def add_note(self, user_id:int, note:Note):
        if note.user_id != user_id:
            raise ValueError("User ID does not match")
        if note.note_id is not None:
            raise ValueError("Note ID must be None")
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        data=self.__serialize_note(note)

        cursor=self.__conn.execute("""
        INSERT INTO note (
            user_id,
            note_type_id,
            fields_JSON,
            tags_JSON,
            sort_field,
            checksum,
            created_at,
            updated_at,
            hint
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            data['note_type_id'],
            data['fields_JSON'],
            data['tags_JSON'],
            data['sort_field'],
            data['checksum'],
            data['created_at'],
            data['updated_at'],
            data['hint'] if data['hint'] is not None else '',
        )
        )
        return cursor.lastrowid

    def get_note(self, user_id:int, note_id:int)->Note:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM note WHERE note_id=? AND user_id=?
        """,(note_id,user_id)).fetchone()
        if row is None:
            raise ValueError("Note not found")
        return self.__deserialize_note(row)
    
    def update_note(self, user_id:int, note:Note):
        if note.user_id != user_id:
            raise ValueError("User ID does not match")
        if note.note_id is None:
            raise ValueError("Note ID is required")
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        data=self.__serialize_note(note)
        cursor=self.__conn.execute("""
            UPDATE note SET
            user_id=?,
            note_type_id=?,
            fields_JSON=?,
            tags_JSON=?,
            sort_field=?,
            checksum=?,
            updated_at=?,
            hint=?
            WHERE note_id=? AND user_id=?
        """,(
            user_id,
            data['note_type_id'],
            data['fields_JSON'],
            data['tags_JSON'],
            data['sort_field'],
            data['checksum'],
            data['updated_at'],
            data['hint'],
            note.note_id,
            user_id,
        ))

        if cursor.rowcount==0:
            raise ValueError("Note not found")
        return self.get_note(user_id, note.note_id)
    
    def delete_note(self, user_id:int, note_id:int):
        if not isinstance(note_id, int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")

        cursor = self.__conn.execute(
            "DELETE FROM note WHERE note_id = ? AND user_id = ?",
            (note_id,user_id),
        )

        if cursor.rowcount == 0:
            raise ValueError("Note not found")

        if cursor.rowcount==0:
            raise ValueError("Note not found")
        return cursor.rowcount

    def get_all_notes(self, user_id:int):
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        rows = self.__conn.execute(
            "SELECT * FROM note WHERE user_id = ? ORDER BY note_id",
            (user_id,),).fetchall()
        return [self.__deserialize_note(row) for row in rows]
    
    def count_notes(self, user_id:int):
        cursor=self.__conn.execute("""
        SELECT COUNT(*) FROM note WHERE user_id = ?
        """,(user_id,))
        return cursor.fetchone()[0]
import json
import sqlite3
from datetime import datetime,date

from ..note.notemodels import Note

class SqliteNoteRepository:
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_note(self,note:Note)->dict:
        return {
            # note_id is auto incremented
            'note_type_id':note.note_type_id,
            'fields_JSON':json.dumps(note.field_json,ensure_ascii=False),
            'tags_JSON':json.dumps(note.tags_json,ensure_ascii=False),
            'sort_field':note.sort_field,
            'checksum':note.checksum,
            'created_at':note.created_at,
            'updated_at':note.updated_at,
        }
    
    def __deserialize_note(self,row:sqlite3.Row)->Note:
        return Note(
            note_id=row['note_id'],
            note_type_id=row['note_type_id'],
            field=json.loads(row['fields_JSON']),
            tags=json.loads(row['tags_JSON']),
            sort_field=row['sort_field'],
            checksum=row['checksum'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
        )
    
    def add_note(self,note:Note):
        if note.note_id is None:
            raise ValueError("Note ID is required")
        data=self.__serialize_note(note)

        cursor=self.__conn.execute("""
        INSERT INTO notes (
            note_type_id,
            fields_JSON,
            tags_JSON,
            sort_field,
            checksum,
            created_at,
            updated_at
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data['note_type_id'],
            data['fields_JSON'],
            data['tags_JSON'],
            data['sort_field'],
            data['checksum'],
            data['created_at'],
            data['updated_at'],
        )
        )
        self.__conn.commit()
        return cursor.lastrowid

    def get_note(self,note_id:int)->Note:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM notes WHERE note_id=?
        """,(note_id,))
        if row is None:
            return ValueError("Note not found")
        return self.__deserialize_note(row)
    
    def update_note(self,note:Note):
        if note.note_id is None:
            raise ValueError("Note ID is required")
        data=self.__serialize_note(note)
        cursor=self.__conn.execute("""
            UPDATE notes SET
            note_type_id=?,
            fields_JSON=?,
            tags_JSON=?,
            sort_field=?,
            checksum=?,
            created_at=?,
            updated_at=?
            WHERE note_id=?
        """,(
            data['note_type_id'],
            data['fields_JSON'],
            data['tags_JSON'],
            data['sort_field'],
            data['checksum'],
            data['created_at'],
            data['updated_at'],
            note.note_id,
        ))

        if cursor.rowcount==0:
            raise ValueError("Note not found")
        self.__conn.commit()
        return cursor.rowcount
    
    def delete_note(self,note_id:int):
        if not isinstance(note_id, int):
            raise TypeError("Note id is not an integer")

        cursor = self.__conn.execute(
            "DELETE FROM note WHERE note_id = ?",
            (note_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError("Note not found")

        self.__conn.commit()
        return "Note deleted successfully"

    def get_all_notes(self):
        rows = self.__conn.execute(
            "SELECT * FROM note ORDER BY note_id"
        ).fetchall()

        return [self.__deserialize_note(row) for row in rows]
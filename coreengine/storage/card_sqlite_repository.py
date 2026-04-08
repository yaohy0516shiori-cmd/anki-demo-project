from ..card.cardmodel import Card
import sqlite3
from datetime import datetime,date
from typing import Optional

class SqliteCardRepository:
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_card(self,card:Card)->dict:
        return {
            'deck_id':card.deck_id,
            'note_id':card.note_id,
            'template_ord':card.template_ord,
            'status':card.status,
            'due':card.due.isoformat(),
            'interval':card.interval,
            'ease':card.ease,
            'reps':card.reps,
            'lapses':card.lapses,
            'step_index':card.step_index,
            'created_at':card.created_at.isoformat(),
            'updated_at':card.updated_at.isoformat(),
        }
    
    def __deserialize_card(self,row:sqlite3.Row)->Card:
        return Card(
            card_id=row['card_id'],
            note_id=row['note_id'],
            deck_id=row['deck_id'],
            template_ord=row['template_ord'],
            status=row['status'],
            # make sure that for due, it is a date object, which is a date object
            due=date.fromisoformat(row['due']),
            interval=int(row['interval']),
            ease=row['ease'],
            reps=int(row['reps']),
            lapses=int(row['lapses']),
            step_index=row['step_index'],
            # make sure that for created_at and updated_at, it is a datetime object 
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
        )
    
    def add_card(self,card:Card):
        if card.card_id is not None:
            raise ValueError("Card ID must be None")
        if card.note_id is None:
            raise ValueError("Note ID is required")
        data=self.__serialize_card(card)
        cursor=self.__conn.execute("""
        INSERT INTO card (
            note_id,
            deck_id,
            template_ord,
            status,
            due,
            interval,
            ease,
            reps,
            lapses,
            step_index,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data['note_id'],
            data['deck_id'],
            data['template_ord'],
            data['status'],
            data['due'],
            data['interval'],
            data['ease'],
            data['reps'],
            data['lapses'],
            data['step_index'],
            data['created_at'],
            data['updated_at'],
        ))
        self.__conn.commit()
        return cursor.lastrowid
    
    def get_card(self,card_id:int)->Card:
        if not isinstance(card_id,int):
            raise ValueError("Card ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM card WHERE card_id=?
        """,(card_id,)).fetchone()
        if row is None:
            raise ValueError("Card not found")
        return self.__deserialize_card(row)

    def update_card(self,card:Card):
        if card.card_id is None:
            raise ValueError("Card ID is required")
        data=self.__serialize_card(card)
        cursor=self.__conn.execute("""
            UPDATE card SET
            note_id=?,
            deck_id=?,
            template_ord=?,
            status=?,
            due=?,
            interval=?,
            ease=?,
            reps=?,
            lapses=?,
            step_index=?,
            updated_at=?
            WHERE card_id=?
        """,(
            data['note_id'],
            data['deck_id'],
            data['template_ord'],
            data['status'],
            data['due'],
            data['interval'],
            data['ease'],
            data['reps'],
            data['lapses'],
            data['step_index'],
            data['updated_at'],
            card.card_id,
        ))
        if cursor.rowcount==0:
            raise ValueError("Card not found")
        self.__conn.commit()
        return cursor.rowcount

    def list_cards_by_note_id(self,note_id:int)->list[Card]:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        rows=self.__conn.execute("""
        SELECT * FROM card WHERE note_id=?
        """,(note_id,)).fetchall()
        if len(rows)==0:
            raise ValueError("Card not found")
        return [self.__deserialize_card(row) for row in rows]
        
    def get_card_by_note_id_and_ord(self,note_id:int,template_ord:int)->Optional[Card]:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(template_ord,int):
            raise ValueError("Template ord must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM card WHERE note_id=? AND template_ord=?
        """,(note_id,template_ord)).fetchone()
        if row is None:
            raise ValueError("Card not found")
        return self.__deserialize_card(row)
        
    def list_cards(self):
        rows=self.__conn.execute("""
        SELECT * FROM card ORDER BY card_id
        """).fetchall()
        return [self.__deserialize_card(row) for row in rows]
    
    def delete_cards_by_note_id(self,note_id:int):
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        cursor=self.__conn.execute("""
        DELETE FROM card WHERE note_id=?
        """,(note_id,))
        if cursor.rowcount==0:
            raise ValueError("Card not found")
        self.__conn.commit()
        return cursor.rowcount
    
    def clear_cards(self):
        self.__conn.execute("""
        DELETE FROM card
        """)
        self.__conn.commit()
        return "Cards cleared successfully"
    
    def count_cards(self):
        row=self.__conn.execute("""
        SELECT COUNT(*) FROM card
        """).fetchone()
        return row[0]

    def delete_card_by_note_id_and_ord(self,note_id:int,template_ord:int):
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(template_ord,int):
            raise ValueError("Template ord must be an integer")
        cursor=self.__conn.execute("""
        DELETE FROM card WHERE note_id=? AND template_ord=?
        """,(note_id,template_ord))
        if cursor.rowcount==0:
            raise ValueError("Card not found")
        self.__conn.commit()
        return cursor.rowcount
    
    def delete_card(self,card_id:int):
        if not isinstance(card_id,int):
            raise ValueError("Card ID must be an integer")
        cursor=self.__conn.execute("""
        DELETE FROM card WHERE card_id=?
        """,(card_id,))
        if cursor.rowcount==0:
            raise ValueError("Card not found")
        self.__conn.commit()
    
    def list_all_cards(self)->list[Card]:
        rows=self.__conn.execute("""
        SELECT * FROM card ORDER BY card_id
        """).fetchall()
        return [self.__deserialize_card(row) for row in rows]
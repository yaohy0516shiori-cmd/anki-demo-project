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
            'created_at':card.created_at,
            'updated_at':card.updated_at,
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
            step_index=int(row['step_index']) if row['step_index'] is not None else None,
            # make sure that for created_at and updated_at, it is a datetime object 
            created_at=row['created_at'],
            updated_at=row['updated_at'],
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
        return self.get_card(cursor.lastrowid)
    
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
        return self.get_card(card.card_id)

    def get_cards_by_note_id(self,note_id:int)->list[Card]:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        rows=self.__conn.execute("""
        SELECT * FROM card WHERE note_id=?
        """,(note_id,)).fetchall()
        if len(rows)==0:
            return []
        result=[self.__deserialize_card(row) for row in rows]
        result.sort(key=lambda card: (card.note_id,card.card_id,card.template_ord))
        return result
        
    def get_cards_by_note_id_and_ord(self,note_id:int,template_ord:int)->Optional[Card]:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(template_ord,int):
            raise ValueError("Template ord must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM card WHERE note_id=? AND template_ord=?
        """,(note_id,template_ord)).fetchone()
        if row is None:
            return []
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
        return f"Deleted {cursor.rowcount} cards successfully"
    
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

    def delete_cards_by_note_id_and_ord(self,note_id:int,template_ord:int):
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
        return f"Deleted {cursor.rowcount} cards successfully"
    
    def delete_card(self,card_id:int):
        if not isinstance(card_id,int):
            raise ValueError("Card ID must be an integer")
        cursor=self.__conn.execute("""
        DELETE FROM card WHERE card_id=?
        """,(card_id,))
        if cursor.rowcount==0:
            raise ValueError("Card not found")
        self.__conn.commit()
        return f"Deleted {cursor.rowcount} card successfully"
    
    def list_all_cards(self)->list[Card]:
        rows=self.__conn.execute("""
        SELECT * FROM card ORDER BY card_id
        """).fetchall()
        return [self.__deserialize_card(row) for row in rows]

    def get_cards_by_deck_id(self,deck_id:int)->list[Card]:
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        rows=self.__conn.execute("""
        SELECT * FROM card WHERE deck_id=?
        """,(deck_id,)).fetchall()
        if len(rows)==0:
            return []
        result=[self.__deserialize_card(row) for row in rows]
        result.sort(key=lambda card: (card.deck_id,card.card_id,card.template_ord))
        return result

    def get_due_cards_by_deck_id(self,deck_id:int,today:date)->list[Card]:
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        rows=self.__conn.execute("""
        SELECT * FROM card WHERE deck_id=? AND due<=? ORDER BY due,note_id,card_id,template_ord
        """,(deck_id,today.isoformat())).fetchall()
        if len(rows)==0:
            return []
        return [self.__deserialize_card(row) for row in rows]
    
    def move_note_cards_to_deck(self,note_id:int,deck_id:int)->list[Card]:
        if not isinstance(note_id,int):
            raise ValueError("Note ID must be an integer")
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        rows=self.__conn.execute("""
        UPDATE card SET deck_id=? WHERE note_id=? AND deck_id!=?
        """,(deck_id,note_id,deck_id))
        if len(rows)==0:
            return []
        self.__conn.commit()
        return rows.rowcount
    
    def move_cards_to_deck(self,from_deck_id:int,to_deck_id:int)->list[Card]:
        if not isinstance(from_deck_id,int) or from_deck_id<=0:
            raise ValueError("From Deck ID must be a positive integer")
        if not isinstance(to_deck_id,int) or to_deck_id<=0:
            raise ValueError("To Deck ID must be a positive integer")
        if from_deck_id==to_deck_id:
            return []
        
        rows=self.__conn.execute("""
        UPDATE card SET deck_id=? WHERE deck_id=?
        """,(to_deck_id,from_deck_id))
        self.__conn.commit()
        return rows.rowcount
import sqlite3
from ..deck.deckmodel import Deck

class SqliteDeckRepository:
    def __init__(self, conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_deck(self,deck:Deck)->dict:
        return {
            'deck_id':deck.deck_id,
            'deck_name':deck.deck_name,
            'deck_description':deck.deck_description,
            'created_at':deck.created_at,
            'updated_at':deck.updated_at,
        }

    def __deserialize_deck(self,data:sqlite3.Row)->Deck:
        return Deck(
            deck_id=data['deck_id'],
            deck_name=data['deck_name'] if data['deck_name'] is not None else '',
            deck_description=data['deck_description'] if data['deck_description'] is not None else '',
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )   
    
    def create_deck(self, deck:Deck):
        if deck.deck_id is not None:
            raise ValueError("Deck ID must be None")
        data=self.__serialize_deck(deck)
        cursor=self.__conn.execute("""
        INSERT INTO deck (
            deck_name,
            deck_description,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?)
        """,
        (
            data['deck_name'], 
            data['deck_description'], 
            data['created_at'], 
            data['updated_at']
        ))
        self.__conn.commit()
        return self.get_deck(cursor.lastrowid)
    
    def get_deck(self, deck_id:int):
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_id=?
        """,(deck_id,)).fetchone()
        if row is None:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(row)
    
    def update_deck(self, deck:Deck):
        if deck.deck_id is None:
            raise ValueError("Deck ID is required")
        data=self.__serialize_deck(deck)
        cursor=self.__conn.execute("""
        UPDATE deck SET
        deck_name=?,
        deck_description=?,
        updated_at=?
        WHERE deck_id=?
        """,
        (
            data['deck_name'],
            data['deck_description'],
            data['updated_at'],
            deck.deck_id
        ))
        if cursor.rowcount==0:
            raise ValueError("Deck not found")
        self.__conn.commit()
        return self.get_deck(deck.deck_id)
    
    def delete_deck(self, deck_id:int):
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        cursor=self.__conn.execute("""
        DELETE FROM deck WHERE deck_id=?
        """,(deck_id,))
        if cursor.rowcount==0:
            raise ValueError("Deck not found")
        self.__conn.commit()
        return "Deck deleted successfully"
    
    def get_all_decks(self):
        cursor=self.__conn.execute("""
        SELECT * FROM deck
        """).fetchall()
        return [self.__deserialize_deck(row) for row in cursor]
    
    def get_all_decks_ids(self):
        cursor=self.__conn.execute("""
        SELECT deck_id FROM deck
        """).fetchall()
        return [row['deck_id'] for row in cursor]
    
    def get_default_deck(self):
        return self.__ensure_default_deck()

    def get_default_deck_id(self):
        return self.__ensure_default_deck().deck_id
    
    def is_default_deck(self, deck_id:int):
        return deck_id==self.get_default_deck_id()
    
    def clear_decks(self):
        cursor=self.__conn.execute("""
        DELETE FROM deck
        """).fetchall()
        self.__conn.commit()
        return "Decks cleared successfully"
    
    def get_deck_by_id(self, deck_id:int):
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_id=?
        """,(deck_id,)).fetchone()
        if row is None:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(row)
    
    def __ensure_default_deck(self):
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_id=1
        """).fetchone()
        if row is None:
            self.__conn.execute("""
            INSERT INTO deck (
            deck_id, 
            deck_name, 
            deck_description, 
            created_at, 
            updated_at) 
            VALUES (1, 
            'Default Deck', 
            'System Default Deck', 
            CURRENT_TIMESTAMP, 
            CURRENT_TIMESTAMP
            )
            """)
            self.__conn.commit()
            return self.get_deck(1)
        return self.__deserialize_deck(row)
    
    def get_deck_by_name(self, deck_name:str):
        if not isinstance(deck_name,str):
            raise ValueError("Deck name must be a string")
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_name=?
        """,(deck_name,)).fetchone()
        if row is None:
            raise ValueError("Deck not found")
        return self.__deserialize_deck(row)
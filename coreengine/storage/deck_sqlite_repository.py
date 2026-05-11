import sqlite3
from ..deck.deckmodel import Deck
from ..deck.deck_repository import DeckRepository
from datetime import datetime, timezone

class SqliteDeckRepository(DeckRepository):
    def __init__(self, conn:sqlite3.Connection):
        self.__conn=conn
    
    def __serialize_deck(self,deck:Deck)->dict:
        return {
            'user_id':deck.user_id,
            'deck_id':deck.deck_id,
            'deck_name':deck.deck_name,
            'deck_description':deck.deck_description,
            'created_at':deck.created_at,
            'updated_at':deck.updated_at,
        }

    def __deserialize_deck(self,data:sqlite3.Row)->Deck:
        return Deck(
            user_id=data['user_id'],
            deck_id=data['deck_id'],
            deck_name=data['deck_name'] if data['deck_name'] is not None else '',
            deck_description=data['deck_description'] if data['deck_description'] is not None else '',
            created_at=data['created_at'],
            updated_at=data['updated_at'],
        )   
    
    def create_deck(self, deck:Deck):
        if deck.deck_id is not None:
            raise ValueError("Deck ID must be None")
        if self.get_deck(deck.user_id, deck.deck_id) is not None:
            raise ValueError("Deck already exists")
        if len(self.get_all_decks(deck.user_id))==0:
            self.create_default_deck(deck.user_id)
        data=self.__serialize_deck(deck)
        cursor=self.__conn.execute("""
        INSERT INTO deck (
            user_id,
            deck_name,
            deck_description,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            data['user_id'],
            data['deck_name'], 
            data['deck_description'], 
            data['created_at'], 
            data['updated_at']
        ))
        return self.get_deck(data['user_id'], cursor.lastrowid)
    
    def get_deck(self, user_id:int, deck_id:int):
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_id=? AND user_id=?
        """,(deck_id,user_id)).fetchone()
        if row is None:
            return None
        return self.__deserialize_deck(row)
    
    def update_deck(self, user_id:int, deck:Deck):
        if deck.deck_id is None:
            raise ValueError("Deck ID is required")
        data=self.__serialize_deck(deck)
        cursor=self.__conn.execute("""
        UPDATE deck SET
        deck_name=?,
        deck_description=?,
        updated_at=?
        WHERE deck_id=? AND user_id=?
        """,
        (
            data['deck_name'],
            data['deck_description'],
            data['updated_at'],
            deck.deck_id,
            user_id
        ))
        if cursor.rowcount==0:
            raise ValueError("Deck not found")
        return self.get_deck(user_id, deck.deck_id)
    
    def delete_deck(self, user_id:int, deck_id:int):
        if not isinstance(deck_id,int):
            raise ValueError("Deck ID must be an integer")
        cursor=self.__conn.execute("""
            DELETE FROM deck WHERE deck_id=? AND user_id=?
        """,(deck_id,user_id))
        if cursor.rowcount==0:
            raise ValueError("Deck not found")
        return cursor.rowcount
    
    def get_all_decks(self, user_id:int):
        cursor=self.__conn.execute("""
        SELECT * FROM deck WHERE user_id=?
        """,(user_id,)).fetchall()
        return [self.__deserialize_deck(row) for row in cursor]
    
    def get_all_decks_ids(self, user_id:int):
        cursor=self.__conn.execute("""
        SELECT deck_id FROM deck WHERE user_id=?
        """,(user_id,)).fetchall()
        return [row['deck_id'] for row in cursor]
    
    def get_default_deck(self, user_id:int):
        return self.__ensure_default_deck(user_id)

    def get_default_deck_id(self, user_id:int):
        return self.__ensure_default_deck(user_id).deck_id
    
    def is_default_deck(self, user_id:int, deck_id:int):
        return deck_id==self.get_default_deck_id(user_id)
    
    def clear_decks(self, user_id:int):
        cursor=self.__conn.execute("DELETE FROM deck WHERE user_id=?",(user_id,))
        self.__ensure_default_deck()
        return cursor.rowcount
    
    def __ensure_default_deck(self, user_id:int):
        row=self.__conn.execute("""
        SELECT * FROM deck WHERE deck_id=1 AND user_id=?
        """,(user_id,)).fetchone()
        if row is None:
            self.__conn.execute("""
            INSERT INTO deck (
            deck_id, 
            deck_name, 
            deck_description, 
            created_at, 
            updated_at) 
            VALUES (1, 
            'Default', 
            'System default deck', 
            CURRENT_TIMESTAMP, 
            CURRENT_TIMESTAMP
            )
            """)
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
    
    def create_default_deck(self, user_id:int):
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        default_data={
            'user_id':user_id,
            'deck_id':1,
            'deck_name':f"Default Deck for User {user_id}",
            'deck_description':f"Default deck for the user {user_id}",
            'created_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            'updated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
        self.__conn.execute("""
            INSERT INTO deck (
            user_id,
            deck_id,
            deck_name,
            deck_description,
            created_at,
            updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                default_data['user_id'],
                default_data['deck_id'],
                default_data['deck_name'],
                default_data['deck_description'],
                default_data['created_at'],
                default_data['updated_at']
            ))
        return self.get_deck(user_id, 1)

class SqliteDeckRepository:
    def __init__(self, conn:sqlite3.Connection):
        self.__conn=conn
    
    def create_deck(self, deck:Deck):
        return self.__repository_deck.create_deck(deck)
    
    def get_deck(self, deck_id:int):
        return self.__repository_deck.get_deck(deck_id)
    
    def update_deck(self, deck:Deck):
        return self.__repository_deck.update_deck(deck)
    
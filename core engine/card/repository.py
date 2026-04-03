from card.cardmodel import Card

# Store cards in memory. will be replaced by database in the future
class InMemoryCardRepository:
    def __init__(self):
        self.__cards={}
        self.__next_id=1
        
    def __serialize_card(self,card:Card):
        # serialize the card to a dictionary
        return {
            "id": card.card_id,
            "note_id": card.note_id,
            "template_ord": card.template_ord,
            "status": card.status,
            "due": card.due,
            "interval": card.interval,
            "ease": card.ease,
            "reps": card.reps,
            "lapses": card.lapses,
            "step_index": card.step_index,
            "created_at": card.created_at,
            "updated_at": card.updated_at
        }

    def __deserialize_card(self,data:dict):
        # deserialize the card from a dictionary
        return Card(
            note_id=data["note_id"],
            template_ord=data["template_ord"],
            card_id=data["id"],
            status=data["status"],
            due=data["due"],
            interval=data["interval"],
            ease=data["ease"],
            reps=data["reps"],
            lapses=data["lapses"],
            step_index=data["step_index"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

    def add_card(self,card:Card):
        # add a card to the repository and assign a new id to the card
        if card.card_id is not None:
            raise ValueError("Card id must be None")
        for data in self.__cards.values():
            if data["note_id"] == card.note_id and data["template_ord"] == card.template_ord:
                raise ValueError("card with same note_id and template_ord already exists")
        card.card_id=self.__next_id
        self.__next_id+=1
        self.__cards[card.card_id]=self.__serialize_card(card)
        return self.__deserialize_card(self.__cards[card.card_id])

    def get_card(self,card_id:int):
        # get a card from the repository by id
        data=self.__cards.get(card_id)
        if data is None:
            return None
        return self.__deserialize_card(data)

    def get_card_by_note_id(self,note_id:int):
        # get all cards from the repository by note id
        result=[]
        for data in self.__cards.values():
            if data["note_id"]==note_id:
                result.append(self.__deserialize_card(data))
        result.sort(key=lambda card: card.template_ord)
        return result

    def get_cards_by_note_id_and_ord(self,note_id:int,template_ord:int):
        # get a card from the repository by note id and template ord
        for data in self.__cards.values():
            if data["note_id"]==note_id and data["template_ord"]==template_ord:
                return self.__deserialize_card(data)
        return None
        
    def list_cards(self):
        # get all cards from the repository
        return (self.__deserialize_card(data) for data in self.__cards.values())

    def update_card(self,card:Card):
        # update a card in the repository
        if card.card_id is None:
            raise ValueError("Card id must be not None")
        if card.card_id not in self.__cards:
            raise ValueError("Card not found")
        self.__cards[card.card_id]=self.__serialize_card(card)
        return self.__deserialize_card(self.__cards[card.card_id])

    def delete_cards_by_note_id(self,note_id:int):
        # delete all cards from the repository by note id
        deleted_id=[]
        for card_id, data in self.__cards.items():
            if data["note_id"]==note_id:
                deleted_id.append(card_id)
        for card_id in deleted_id:
            del self.__cards[card_id]
        return deleted_id
    
    def delete_cards_by_note_id_and_ord(self,note_id:int,template_ord:int):
        # delete all cards from the repository by note id and template ord
        deleted_id=[]
        for card_id, data in self.__cards.items():
            if data["note_id"]==note_id and data["template_ord"]==template_ord:
                deleted_id.append(card_id)
        for card_id in deleted_id:
            del self.__cards[card_id]
        return deleted_id
    
    def delete_card(self,card_id:int):
        # delete a card from the repository by card id
        if card_id not in self.__cards:
            raise ValueError("Card not found")
    def clear_cards(self):
        # clear all cards from the repository
        # safety check
        self.__cards.clear()
        return True
    
    def count_cards(self):
        # count the number of cards in the repository
        return len(self.__cards)
    
    '''
    get_card_by_note_and_ord(note_id, template_ord)
    get_cards_by_state(state)
    get_due_cards(today)
    '''
from card.cardmodel import Card
class InMemoryCardRepository:
    def __init__(self):
        self.__cards={}
        self.__next_id=1
        
    def __serialize_card(self,card:Card):
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
            "created_at": card.created_at,
            "updated_at": card.updated_at
        }

    def __deserialize_card(self,data:dict):
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
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

    def add_card(self,card:Card):
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
        data=self.__cards.get(card_id)
        if data is None:
            return None
        return self.__deserialize_card(data)

    def get_card_by_note_id(self,note_id:int):
        result=[]
        for data in self.__cards.values():
            if data["note_id"]==note_id:
                result.append(self.__deserialize_card(data))
        result.sort(key=lambda card: card.template_ord)
        return result

    def list_cards(self):
        # when should we use list to protect orginal data?
        return (self.__deserialize_card(data) for data in self.__cards.values())

    def update_card(self,card:Card):
        if card.card_id is None:
            raise ValueError("Card id must be not None")
        if card.card_id not in self.__cards:
            raise ValueError("Card not found")
        self.__cards[card.card_id]=self.__serialize_card(card)
        return self.__deserialize_card(self.__cards[card.card_id])
    
    def delete_card(self,card_id:int):
        if card_id not in self.__cards:
            raise ValueError("Card not found")
        del self.__cards[card_id]
        return True
    
    def clear_cards(self):
        self.__cards.clear()
        return True
    
    def count_cards(self):
        return len(self.__cards)
    
    '''
    get_card_by_note_and_ord(note_id, template_ord)
    get_cards_by_state(state)
    get_due_cards(today)
    '''
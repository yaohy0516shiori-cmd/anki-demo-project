from card.cardmodel import Card
class InMemoryRepository_card:
    def __init__(self):
        self.__cards={}
        self.__next_id=1
        
    def __serialize_card(self,card:Card):
        return {
            "id": card.card_id,
            "note_id": card.note_id,
            "temp_ord": card.temp_ord,
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
            temp_ord=data["temp_ord"],
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
        return result

    
from pydantic import BaseModel
from pesten.pesten import card_string



class LobbyCreate(BaseModel):
    name: str
    size: int
    aiCount: int = 0
    two: str = ""
    three: str = ""
    four: str = ""
    five: str = ""
    six: str = ""
    seven: str = ""
    eight: str = ""
    nine: str = ""
    ten: str = ""
    jack: str = ""
    queen: str = ""
    king: str = ""
    ace: str = ""


class LobbyResponse(BaseModel):
    id: str
    size: int
    capacity: int
    creator: str
    players: list[str]



class Card(BaseModel):
    suit: str
    value: str

    @classmethod
    def from_int(cls, card):
        suit, value = card_string(card).split(' ')
        return cls(suit=suit, value=value)


class Board(BaseModel):
    topcard: Card
    can_draw: bool
    current_player: str
    otherPlayers: dict[str, int]
    hand: list[Card]
    message: str

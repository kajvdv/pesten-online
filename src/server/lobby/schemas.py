from typing import Optional

from pydantic import BaseModel
from pesten.pesten import card_string, RED_JOKER, BLACK_JOKER



class LobbyCreate(BaseModel):
    name: str
    size: int
    aiCount: int = 0
    jokerCount: int = 0
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
        if card == RED_JOKER:
            return cls(suit='red', value='joker')
        if card == BLACK_JOKER:
            return cls(suit='black', value='joker')
        suit, value = card_string(card).split(' ')
        return cls(suit=suit, value=value)


class Board(BaseModel):
    topcard: Card
    previous_topcard: Optional[Card] = None
    can_draw: bool
    choose_suit: bool
    draw_count: int = 0
    current_player: str
    otherPlayers: dict[str, int]
    hand: list[Card]
    message: str

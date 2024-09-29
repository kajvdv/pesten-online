from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, status

from pesten.pesten import Pesten, card, card_string, CannotDraw
from pesten.auth import get_current_user, User


class Card(BaseModel):
    suit: str
    value: str

    def __init__(self, card):
        suit, value = card_string(card).split(' ')
        super().__init__(suit=suit, value=value)


class Board(BaseModel):
    topcard: Card
    can_draw: bool
    current_player: str
    hand: list[Card]


class Game:
    def __init__(self, capacity, creator) -> None:
        self.game = Pesten(capacity, 8, [card(suit, value) for suit in range(4) for value in range(13)])
        self.started = False
        self.connections: dict[str, WebSocket] = {}
        self.names = [creator]
        self.capacity = capacity


    async def add_connection(self, name, websocket: WebSocket):
        if name in self.names:
            print("rejoining", name)
        elif self.started:
            raise Exception("Lobby is full")
        elif name in self.names:
            raise Exception("Player already in lobby")
        else:
            self.names.append(name)
        self.connections[name] = websocket
        if len(self.names) == self.capacity:
            self.started = True
        await self.update_boards()
    

    async def send_hand(self, name):
        player_id = self.names.index(name)
        hand = "\n".join([
            str(index) + ": " + card_string(card)
            for index, card in enumerate(self.game.hands[player_id], start=1)
        ])
        websocket = self.connections[name]
        await websocket.send_text(hand)


    async def update_boards(self):
        for name, conn in self.connections.items():
            player_id = self.names.index(name)
            board = Board(
                topcard=Card(self.game.play_stack[-1]),
                can_draw=bool(self.game.draw_stack),
                current_player=self.names[self.game.current_player],
                hand=[Card(card) for card in self.game.hands[player_id]]
            )
            await conn.send_json(board.model_dump())


    async def get_choose(self, name):
        websocket: WebSocket = self.connections[name]
        choose = await websocket.receive_text()
        print(f"New message from {name} in lobby {list(lobbies.values()).index(self)}")
        if not self.started:
            await websocket.send_json({"error": "Game not started"})
            return
        if self.game.current_player != self.names.index(name):
            await websocket.send_json({"error": "Not your turn"})
            return
        
        try:
            choose = int(choose)
        except ValueError:
            await websocket.send_json({"error": "Invalid choose"})
            return
        self.game.play_turn(choose)
        await self.update_boards()




async def game_loop(websocket: WebSocket, name, lobby: Game):
    await lobby.add_connection(name, websocket)
    try:
        while True:
            await lobby.get_choose(name)
    except WebSocketDisconnect:
        print(f"websocket with id disconnected")
    except Exception as e:
        print("ERROR", e)
        await websocket.close()
    finally:
        del lobby.connections[name]




class LobbyCreate(BaseModel):
    size: int

lobbies = {}
router = APIRouter()

class LobbyResponse(BaseModel):
    id: int
    size: int
    capacity: int
    creator: str

@router.get('', response_model=list[LobbyResponse])
def get_lobbies(user: User = Depends(get_current_user)):
    return sorted([{
        'id': id,
        'size': len(lobby.connections),
        'capacity': lobby.capacity,
        'creator': lobby.names[0],
    } for id, lobby in lobbies.items()], key=lambda lobby: lobby['creator'] != user.username)


@router.post('', response_model=list[LobbyResponse])
def create_lobby(lobby: LobbyCreate, user: User = Depends(get_current_user)):
    id = 0
    while(id in lobbies):
        id = id + 1
    size = lobby.size
    new_lobby = Game(size, user.username)
    lobbies[id] = new_lobby
    return get_lobbies(user)

@router.delete('/{id}', response_model=list[LobbyResponse])
def delete_lobby(id: int, user: User = Depends(get_current_user)):
    try:
        lobby_to_be_deleted = lobbies[id]
    except KeyError as e:
        print(f'Lobby with id of {e} does not exist')
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
    if lobby_to_be_deleted.names[0] != user.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you")
    print("deleting lobby")
    lobbies.pop(id)
    return get_lobbies(user)


@router.websocket("/connect")
async def connect_to_lobby(websocket: WebSocket, lobby_id: int = 0, name: str = Depends(get_current_user)):
    print("Websocket connect with", name)
    lobby = lobbies[lobby_id]
    await websocket.accept()
    await game_loop(websocket, name.username, lobby)



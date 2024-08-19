from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

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


class Lobby:
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
        print(f"New message from {name} in lobby {lobbies.index(self)}")
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




async def game_loop(websocket: WebSocket, name, lobby: Lobby):
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

lobbies = []
router = APIRouter()

@router.get('')
def get_lobbies():
    return [{'size': len(lobby.connections), 'capacity': lobby.capacity} for lobby in lobbies]


@router.post('')
def create_lobby(lobby: LobbyCreate, user: User = Depends(get_current_user)):
    id = len(lobbies)
    size = lobby.size
    new_lobby = Lobby(size, user.username)
    lobbies.append(new_lobby)
    print("lobby created", id)
    print(lobbies)
    return id


@router.websocket("/connect")
async def connect_to_lobby(websocket: WebSocket, name: str = Depends(get_current_user), lobby_id: int = 0):
    print("Websocket connect with", name)
    lobby = lobbies[lobby_id]
    await websocket.accept()
    await game_loop(websocket, name.username, lobby)


from urllib.parse import parse_qs
from fastapi import APIRouter, WebSocket, Query
from starlette.endpoints import WebSocketEndpoint
from pydantic import BaseModel

from pesten import create_board
from auth import get_user_from_token


router = APIRouter()

class Lobby:
    def __init__(self, size) -> None:
        self.size = size
        self.connections = {}
        self.game = None

    async def update_websockets(self):
        for i, (name, socket) in enumerate(self.connections.items()):
            print(i, name, socket)
            await socket.send_json({
                'can_draw': True,
                'hand': [str(card) for card in self.game.players.players[i].hand],
                'top_card': str(self.game.playdeck.cards[-1]),
                'currentPlayer': self.game.players.index_current_player,
                'playerId': i,
            })

    async def add_connection(self, name, websocket):
        if name in self.connections:
            try:
                await self.connections[name].close()
            except RuntimeError:
                print("Websocket already disconnected")
        self.connections[name] = websocket
        if len(self.connections) == self.size and not self.game:
            self.game = create_board([name for name in self.connections])
            while(len(self.game.players.current_player.hand) > 1):
                self.game.play(0)
        if self.game:
            await self.update_websockets()

    def get_current_player_name(self):
        return self.game.players.current_player.name


lobbies: list[Lobby] = [Lobby(2)]


class LobbyCreate(BaseModel):
    size: int



@router.get('')
def get_lobbies():
    return [{"size": lobby.size, 'connections': len(lobby.connections)} for lobby in lobbies]


@router.post('')
def create_lobby(lobby: LobbyCreate):
    id = len(lobbies)
    lobbies.append(Lobby(lobby.size))
    return id


# @router.websocket('/game')
# async def gameloop(websocket: WebSocket, token = Query()):
#     # Auth the token
#     print(token)
#     await websocket.accept()
#     ...

"""
Ik wil af van die Starlette websocket om zo weer de FastAPI features te kunnen gebruiken.
De feature die ik wil is om Query te gebruiken om makkelijk aan de query parameters te komen.
Het was alleen gezeik wanneer ik naar meerdere websockets te gelijk wilde luisteren.
Moet nog bedenken hoe ik dit ga doen.
"""

@router.websocket_route('/game')
class Gameloop(WebSocketEndpoint):
    encoding = 'text'

    async def on_connect(self, websocket, **kwargs): 
        global lobbies
        await websocket.accept()
        params = websocket.scope['query_string']
        params = params.decode('utf-8')
        params = parse_qs(params)
        token = params.get('token')
        name = get_user_from_token(token[0])
        # name = name[0]
        lobby_id = int(params.get('lobby_id')[0])
        print(f'new connection for {name} on {lobby_id}')
        self.lobby = lobbies[lobby_id]
        self.name = name
        await self.lobby.add_connection(name, websocket)
        
    async def on_receive(self, websocket, data): 
        if self.name != self.lobby.get_current_player_name():
            print("not your turn", self.name, self.lobby.get_current_player_name())
            return
        choose = int(data)
        self.lobby.game.play_turn(choose)
        await self.lobby.update_websockets()
        if self.lobby.game.has_won():
            print("Game won by", self.lobby.game.players.current_player.name)
            sockets = self.lobby.connections.values()
            lobbies.remove(self.lobby)
            for socket in sockets:
                await socket.close()


    async def on_disconnect(self, websocket, close_code): 
        print("closing with code", close_code)
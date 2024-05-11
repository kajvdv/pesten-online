from fastapi import APIRouter
from pydantic import BaseModel

from pesten import create_board


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
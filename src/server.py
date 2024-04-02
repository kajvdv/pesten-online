"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import subprocess
import sys
import asyncio
import select
from urllib.parse import parse_qs

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint
from pydantic import BaseModel
import uvicorn
from pesten import Board, create_board
import json


app = FastAPI()


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
        self.connections[name] = websocket
        if len(self.connections) == self.size:
            self.game = create_board([name for name in self.connections])
            await self.update_websockets()

    def get_current_player_name(self):
        return self.game.players.current_player.name


lobbies: list[Lobby] = [Lobby(2)]


class LobbyCreate(BaseModel):
    size: int


@app.get('/lobbies')
def get_lobbies():
    return [{"size": lobby.size, 'connections': len(lobby.connections)} for lobby in lobbies]


@app.post('/lobbies')
def create_lobby(lobby: LobbyCreate):
    id = len(lobbies)
    lobbies.append(Lobby(lobby.size))
    return id


@app.websocket_route('/pesten')
class Gameloop(WebSocketEndpoint):
    encoding = 'text'

    async def on_connect(self, websocket, **kwargs): 
        global lobbies
        await websocket.accept()
        params = websocket.scope['query_string']
        params = params.decode('utf-8')
        params = parse_qs(params)
        name = params.get('name', ['anonymous'])
        name = name[0]
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


    async def on_disconnect(self, websocket, close_code): 
        print("closing with code", close_code)

@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

app.mount("/static", StaticFiles(directory="src/static"), name="static")


if __name__ == "__main__":
    uvicorn.run(app)
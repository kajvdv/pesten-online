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
from fastapi.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint
import uvicorn
from pesten import Board, create_board
import json


app = FastAPI()

game: Board = None
sockets: list[WebSocket] = []


def play_turn(game, choose):
    if choose == -1:
        game.draw()
        game.next()
    else:
        if game.check(choose):
            game.play(choose)
            game.next()


@app.websocket_route('/')
class Gameloop(WebSocketEndpoint):
    encoding = 'text'

    async def update_websockets(self):
        for i, socket in enumerate(sockets):
            await socket.send_json({
                'can_draw': True,
                'hand': [str(card) for card in game.players.players[i].hand],
                'top_card': str(game.playdeck.cards[-1]),
                'currentPlayer': game.players.index_current_player,
                'playerId': i,
            })

    async def on_connect(self, websocket, **kwargs): 
        global game
        self.player_id = len(sockets)
        await websocket.accept()
        name = websocket.scope['query_string']
        name = name.decode('utf-8')
        name = parse_qs(name)
        name = name.get('name', ['anonymous'])
        name = name[0]
        print('new connection for', name)
        sockets.append(websocket)
        if len(sockets) == 2:
            print("creating game")
            game = create_board(['kaj', 'soy'])
            await self.update_websockets()
        
    async def on_receive(self, websocket, data): 
        global game
        print(self.player_id, game.players.index_current_player)
        if self.player_id != game.players.index_current_player:
            print("not your turn")
            return
        choose = int(data)
        play_turn(game, choose)
        await self.update_websockets()


    async def on_disconnect(self, websocket, close_code): 
        print("closing with code", close_code)

app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
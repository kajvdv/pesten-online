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
from websocket import create_connection
from pesten.game import Board, create_board
import json


app = FastAPI()

game: Board = None
sockets: list[WebSocket] = []
current_index = 0
on_turns: list[asyncio.Event] = []


@app.websocket('/')
async def connect_to_game(websocket: WebSocket, name):
    global current_index
    global game
    player_id = len(sockets)
    await websocket.accept()
    print('new connection for', name)
    sockets.append(websocket)
    on_turns.append(asyncio.Event())
    # Telling the first player to make a move
    if len(sockets) == 2:
        game = create_board(['kaj', 'soy'])
        on_turns[0].set()
    while(True): 
        await on_turns[player_id].wait()
        print(name, "their turn")
        try:
            for i, socket in enumerate(sockets):
                await socket.send_json({
                    'can_draw': True,
                    'hand': [str(card) for card in game.players.players[i].hand],
                    'top_card': str(game.playdeck.cards[-1]),
                    'currentPlayer': current_index,
                    'playerId': i,
                })
            choose = await websocket.receive_text()
        except (WebSocketDisconnect, RuntimeError):
            print("Disconnecting websocket", name)
            on_turns[(player_id+1) % len(on_turns)].set()
            break

        if choose == '-1':
            game.draw()
            game.next()
        else:
            index = int(choose)
            if game.check(index):
                game.play(int(choose))
                game.next()
        current_index = game.players.index_current_player

        on_turns[player_id].clear()
        on_turns[current_index].set()


@app.websocket_route('/class')
class Gameloop(WebSocketEndpoint):
    encoding = 'text'

    async def on_connect(self, websocket, **kwargs): 
        player_id = len(sockets)
        await websocket.accept()
        name = websocket.scope['query_string']
        name = name.decode('utf-8')
        name = parse_qs(name)
        name = name.get('name', ['anonymous'])
        name = name[0]
        print('new connection for', name)
        sockets.append(websocket)
        on_turns.append(asyncio.Event())
        if len(sockets) == 2:
            print("creating game")
            game = create_board(['kaj', 'soy'])
            for i, socket in enumerate(sockets):
                print("sending message")
                await socket.send_json({
                    'can_draw': True,
                    'hand': [str(card) for card in game.players.players[i].hand],
                    'top_card': str(game.playdeck.cards[-1]),
                    'currentPlayer': current_index,
                    'playerId': i,
                })
        
    async def on_receive(self, websocket, data): 
        choose = data
        print(choose)


    async def on_disconnect(self, websocket, close_code): 
        ...

app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
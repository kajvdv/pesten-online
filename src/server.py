"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import subprocess
import sys
import asyncio
import select

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTasks
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
        

app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
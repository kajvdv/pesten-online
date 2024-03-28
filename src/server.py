"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import subprocess
import sys
import asyncio
import select

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
from websocket import create_connection
from pesten.game import Board, create_board
import json


app = FastAPI()

game: Board = None
sockets: list[WebSocket] = []
flags: list[asyncio.Event] = []
chooses: dict[WebSocket, asyncio.Queue] = {}
current_index = 0
on_turns: list[asyncio.Event] = []


# async def get_choose(game):
#     global current_index
#     websocket = sockets[current_index]
#     print("getting choose for i", current_index)
#     await websocket.send_json({
#         'can_draw': True,
#         'hand': game['players'][current_index]['hand'],
#         'top_card': game['playDeck'][-1],
#         'currentPlayer': current_index,
#         'playerId': current_index,
#     })
#     choose = await websocket.receive_text()
#     return int(choose) + 1


# async def send_message(message):
#     global current_index
#     websocket = sockets[current_index]
#     await websocket.send({
#         "drawDeck": [],
#         "playDeck": [],
#         "players": [],
#         "currentPlayer": "",
#         "message": message,
#     })
    

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
        for i, socket in enumerate(sockets):
            await socket.send_json({
                'can_draw': True,
                'hand': [str(card) for card in game.players.players[i].hand],
                'top_card': str(game.playdeck.cards[-1]),
                'currentPlayer': current_index,
                'playerId': i,
            })
        choose = await websocket.receive_text()
        if choose == '-1':
            game.draw()
        else:
            game.play(int(choose))
        current_index = game.next()

        on_turns[player_id].clear()
        on_turns[current_index].set()
    


app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
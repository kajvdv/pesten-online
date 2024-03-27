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
from pesten.main import play_game
import json


app = FastAPI()

sockets: list[WebSocket] = []
flags: list[asyncio.Event] = []
chooses: dict[WebSocket, asyncio.Queue] = {}
current_index = 0
on_turns: list[asyncio.Event] = []


def create_get_choose(websocket: WebSocket):
    async def get_choose(game):
        i = sockets.index(websocket)
        print("getting choose for i", i)
        await websocket.send_json({
                'can_draw': True,
                'hand': game['players'][i]['hand'],
                'top_card': game['playDeck'][-1],
                'currentPlayer': current_index,
                'playerId': i,
            })
        return await websocket.receive_text()


    return get_choose


def create_send_message(websocket):
    async def send_message(message):
        await websocket.send({
            "drawDeck": [],
            "playDeck": [],
            "players": [],
            "currentPlayer": "",
            "message": message,
        })
    
    return send_message


@app.websocket('/')
async def connect_to_game(websocket: WebSocket, name):
    global current_index
    player_id = len(sockets)
    await websocket.accept()
    print('new connection for', name)
    sockets.append(websocket)
    on_turns.append(asyncio.Event())
    # Telling the first player to make a move
    if len(sockets) == 2:
        on_turns[0].set()
        await play_game(['Kaj', 'Soy'], create_get_choose(websocket), create_send_message(websocket))
    while(True): 
        await on_turns[player_id].wait()

        # board = game_process.stdout.readline().strip()
        # if 'won' in board:
        #     print("Einde spel:", board)
        #     break
        # print("read output game!", board)
        # board = json.loads(board)
        # # Dit moet uiteindelijk naar alle spelers worden gestuurd
        # #TODO: Have all players update their boards
        # for i, socket in enumerate(sockets):
        #     await socket.send_json({
        #         'can_draw': True,
        #         'hand': board['players'][i]['hand'],
        #         'top_card': board['topCard'],
        #         'currentPlayer': current_index,
        #         'playerId': i,
        #     })

        # choose = await websocket.receive_text()
        # answer = int(choose) + 1
        # game_process.stdin.write(str(answer) + '\n')
        # game_process.stdin.flush()
        # current_index = int(game_process.stdout.readline().strip())
        # print("next player is", current_index)

        on_turns[player_id].clear()
        on_turns[current_index].set()
    


app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
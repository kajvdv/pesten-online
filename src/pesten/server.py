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

game_process = subprocess.Popen([sys.executable, '-m', 'pesten.main'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
sockets: list[WebSocket] = []
flags: list[asyncio.Event] = []
chooses: dict[WebSocket, asyncio.Queue] = {}
current_index = 0
on_turns: list[asyncio.Event] = []


@app.websocket('/')
async def connect_to_game(websocket: WebSocket, name):
    player_id = len(sockets)
    await websocket.accept()
    print('new connection for', name)
    sockets.append(websocket)
    on_turns.append(asyncio.Event())
    # Telling the first player to make a move
    if len(sockets) == 2:
        on_turns[0].set()
    while(True):
        await on_turns[player_id].wait()

        board = game_process.stdout.readline().strip()
        if 'won' in board:
            print("Einde spel:", board)
            break
        print("read output game!", board)
        board = json.loads(board)
        # Dit moet uiteindelijk naar alle spelers worden gestuurd
        #TODO: Have all players update their boards
        await websocket.send_json({
            'can_draw': True,
            'hand': board['hand'],
            'top_card': board['topCard']
        })

        choose = await websocket.receive_text()
        answer = int(choose) + 1
        game_process.stdin.write(str(answer) + '\n')
        game_process.stdin.flush()
        current_index = int(game_process.stdout.readline().strip())

        on_turns[current_index].set()
        on_turns[player_id].clear()
    


app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
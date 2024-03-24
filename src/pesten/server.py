"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import subprocess
import sys

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
from pesten.main import play_game
import json

""""""

app = FastAPI()

sockets: list[WebSocket] = []

@app.websocket('/')
async def connect_to_lobby(websocket: WebSocket, name):
    await websocket.accept()
    print('new connection for', name)
    game_process = subprocess.Popen([sys.executable, '-m', 'pesten.main'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    while(True):
        board = game_process.stdout.readline().strip()
        if 'won' in board:
            print("Einde spel:", board)
            break
        print("read output game!", board)
        board = json.loads(board)
        await websocket.send_json({
            'can_draw': True,
            'hand': board['hand'],
            'top_card': board['topCard']
        })
        answer = await websocket.receive_text()
        answer = int(answer) + 1
        game_process.stdin.write(str(answer) + '\n')
        game_process.stdin.flush()


app.mount("/", StaticFiles(directory="src/board"), name="board")


if __name__ == "__main__":
    uvicorn.run(app)
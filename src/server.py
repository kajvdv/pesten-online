"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import subprocess
import sys
import asyncio
import select
from urllib.parse import parse_qs

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint
from pydantic import BaseModel
import uvicorn
from pesten import Board, create_board
from lobby import router as router_lobby
from auth import router as router_auth, get_current_user
import json



app = FastAPI()
# Secure endpoints with Depends(get_current_user)
app.include_router(router_lobby, prefix='/lobbies', dependencies=[Depends(get_current_user)])
app.include_router(router_auth)

#TODO move to the lobbies endpoint
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
        if self.lobby.game.has_won():
            print("Game won by", self.lobby.game.players.current_player.name)
            sockets = self.lobby.connections.values()
            lobbies.remove(self.lobby)
            for socket in sockets:
                await socket.close()


    async def on_disconnect(self, websocket, close_code): 
        print("closing with code", close_code)

@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(app)
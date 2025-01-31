"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from server.lobby.routes import router as router_lobby
from server.auth import router as router_auth


app = FastAPI()
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
)


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

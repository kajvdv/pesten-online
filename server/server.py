"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
from pathlib import Path
import asyncio
import pickle
import random
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, PlainTextResponse

from server.lobby.routes import router as router_lobby, lobbies_create_parameters
from server.auth import router as router_auth, ExpiredSignatureError
from server.admin import router as router_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    from server.reload import save_lobbies, load_lobbies
    from server.lobby.dependencies import get_lobbies
    
    lobbies = get_lobbies()
    await load_lobbies(lobbies, lobbies_create_parameters)
    yield
    save_lobbies(lobbies, lobbies_create_parameters)




app = FastAPI(
    lifespan=lifespan
)
app.debug = True
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
)
app.include_router(router_admin, prefix='/admin')

@app.exception_handler(ExpiredSignatureError)
def handle_expired_auth(request, exc):
    return PlainTextResponse("Unauthorized", status_code=401)


@app.get('/tasks')
async def get_tasks():
    tasks = asyncio.all_tasks()
    for task in tasks:
        print(task.get_name(), task.get_coro())


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

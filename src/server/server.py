"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import asyncio
import random
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from server.lobby.routes import router as router_lobby
from server.lobby.dependencies import Lobbies
from server.auth import router as router_auth
from server.admin import router as router_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    from server.lobby.dependencies import get_lobbies, Player, AIConnection, NullConnection, Lobby, Pesten, card, connect_ais
    import random

    game = Lobby(Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {77: 'draw_card-5', 78: 'draw_card-5'}), 'admin')
    lobbies_crud = Lobbies('admin', get_lobbies())
    await lobbies_crud.create_lobby('jokers', 1, game)

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Lobby(Pesten(4, 8, cards, {
        9: 'change_suit',
        0: 'draw_card-2',
        5: 'another_turn',
        6: 'skip_turn',
        12: 'reverse_order',
    }), 'admin')
    await lobbies_crud.create_lobby("met regels", 3, game)

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Lobby(Pesten(6, 8, cards, {
        0: 'draw_card-3',
        1: 'draw_card-3',
        2: 'draw_card-3',
        3: 'draw_card-3',
        4: 'draw_card-3',
        5: 'draw_card-3',
        6: 'draw_card-3',
        7: 'draw_card-3',
        8: 'draw_card-3',
        9: 'draw_card-3',
        10: 'draw_card-3',
        11: 'draw_card-3',
        12: 'draw_card-3',
    }), 'admin')
    await lobbies_crud.create_lobby("Alleen maar pakken", 5, game)
    yield


app = FastAPI(
    lifespan=lifespan if "--init-lobbies" in sys.argv else None
)
app.debug = True
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
)
app.include_router(router_admin, prefix='/admin')


@app.get('/tasks')
async def get_tasks():
    tasks = asyncio.all_tasks()
    for task in tasks:
        print(task.get_name())


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

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
from server.auth import router as router_auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    from server.lobby.dependencies import get_lobbies, Player, AIConnection, NullConnection, Lobby, Pesten, card, connect_ais

    lobby_name = "jokers"
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Lobby(Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {}), 'admin')
    get_lobbies()[lobby_name] = game
    asyncio.create_task(game.connect(Player(f'admin', NullConnection())))
    asyncio.create_task(connect_ais(game, 1))
    game = Lobby(Pesten(2, 8, cards, {
        9: 'change_suit',
        0: 'draw_card-2',
        5: 'another_turn',
        6: 'skip_turn',
        12: 'reverse_order',
    }), 'admin')

    lobby_name = "met regels"
    get_lobbies()[lobby_name] = game
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'admin', NullConnection())))
    asyncio.create_task(connect_ais(game, 1))

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    lobby_name = "Alleen maar pakken"
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
    asyncio.create_task(game.connect(Player(f'admin', NullConnection())))
    get_lobbies()[lobby_name] = game
    asyncio.create_task(connect_ais(game, 5))
    yield


app = FastAPI(
    lifespan=lifespan if "--init-lobbies" in sys.argv else None
)
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
)


@app.get('/tasks')
async def get_tasks():
    tasks = asyncio.all_tasks()
    for task in tasks:
        print(task.get_name())


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

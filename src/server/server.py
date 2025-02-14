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


@asynccontextmanager
async def lifespan(app: FastAPI):
    from server.lobby.dependencies import get_lobbies, Player, AIConnection, NullConnection, Lobby, Pesten, card
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    lobby_name = "met regels"
    get_lobbies()['jokers'] = Lobby(Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {}), 'admin')
    asyncio.create_task(get_lobbies()['jokers'].connect(Player(f'admin', NullConnection())))
    asyncio.create_task(get_lobbies()['jokers'].connect(Player(f'test AI1', AIConnection(get_lobbies()['jokers'].game, 1))))
    get_lobbies()[lobby_name] = Lobby(Pesten(2, 8, cards, {
        9: 'change_suit',
        0: 'draw_card',
        5: 'another_turn',
        6: 'skip_turn',
        12: 'reverse_order',
    }), 'admin')
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'admin', NullConnection())))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI1', AIConnection(get_lobbies()[lobby_name].game, 1))))
    # asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI2', AIConnection(get_lobbies()[lobby_name].game, 2))))
    # asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI3', AIConnection(get_lobbies()[lobby_name].game, 3))))
    # asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI4', AIConnection(get_lobbies()[lobby_name].game, 4))))
    # asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI5', AIConnection(get_lobbies()[lobby_name].game, 5))))

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    lobby_name = "Alleen maar pakken"
    get_lobbies()[lobby_name] = Lobby(Pesten(6, 8, cards, {
        0: 'draw_card',
        1: 'draw_card',
        2: 'draw_card',
        3: 'draw_card',
        4: 'draw_card',
        5: 'draw_card',
        6: 'draw_card',
        7: 'draw_card',
        8: 'draw_card',
        9: 'draw_card',
        10: 'draw_card',
        11: 'draw_card',
    }), 'admin')
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'admin', NullConnection())))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI1', AIConnection(get_lobbies()[lobby_name].game, 1))))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI2', AIConnection(get_lobbies()[lobby_name].game, 2))))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI3', AIConnection(get_lobbies()[lobby_name].game, 3))))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI4', AIConnection(get_lobbies()[lobby_name].game, 4))))
    asyncio.create_task(get_lobbies()[lobby_name].connect(Player(f'test AI5', AIConnection(get_lobbies()[lobby_name].game, 5))))
    yield


app = FastAPI(lifespan=lifespan)
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
)


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

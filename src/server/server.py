"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
import asyncio
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from server.lobby import router as router_lobby, Pesten, AIConnection, game_loop
from pesten.game import card
from server.auth import router as router_auth
import server.lobby as lobby


@asynccontextmanager
async def lifespan(app: FastAPI):
    await lobby.lobbies['test game'].add_connection('AI', AIConnection(pesten, 1))
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

cards = [card(suit, value) for suit in range(4) for value in range(13)]
# random.seed(1)
random.shuffle(cards)
pesten = Pesten(2, 8, cards)

game = lobby.Game(pesten, 'admin')
lobby.lobbies = {'test game': game}

"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from server.lobby import router as router_lobby, Pesten
from pesten.game import card
from server.auth import router as router_auth
import server.lobby as lobby



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


game = Pesten(2, 1, [
    # card(suit, value) for suit in range(4) for value in range(13)
    card(0, 0),
    card(0, 0),
    card(0, 0),
    card(0, 0),
])
lobby.lobbies = {'test game': lobby.Game(game, 'admin')}

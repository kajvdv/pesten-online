"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from pesten.lobby import router as router_lobby, get_current_user_websocket, Pesten
from pesten.game import card
from pesten.auth import router as router_auth, get_current_user, User
import pesten.lobby



app = FastAPI()
# Secure endpoints with Depends(get_current_user)
app.include_router(router_auth)
app.include_router(
    router_lobby,
    prefix='/lobbies',
    # dependencies=[Depends(get_current_user)]
)


@app.get('/')
def get_static():
    return RedirectResponse('/static/home.html')

# app.mount("/static", StaticFiles(directory="static"), name="static")

game = Pesten(2, 1, [
    # card(suit, value) for suit in range(4) for value in range(13)
    card(0, 0),
    card(0, 0),
    card(0, 0),
    card(0, 0),
])
pesten.lobby.lobbies = {0: pesten.lobby.Game(game, 'admin')}

def get_current_user_override(name: str = 'admin'):
    # stmt = select(User)
    # for db in get_db():
    #     row = db.execute(stmt).first()
    # return row.User
    user = User(username=name, password="")
    print("logging in as", user.username)
    return user.username

app.dependency_overrides[get_current_user] = get_current_user_override
app.dependency_overrides[get_current_user_websocket] = lambda name: name

if __name__ == "__main__":
    uvicorn.run(app)
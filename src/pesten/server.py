"""The player connects to a game using websockets. 
Every websockets represents a player, so every game has multiple websocket connections.
Players can create new games using the post endpoint, to which they can connect using a websocket.

"""
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from pesten.lobby import router as router_lobby
from pesten.auth import router as router_auth, get_current_user


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


if __name__ == "__main__":
    uvicorn.run(app)
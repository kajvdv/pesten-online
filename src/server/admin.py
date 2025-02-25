from fastapi import FastAPI, Depends, HTTPException, APIRouter

from server.auth import get_current_user, get_token
from server.lobby.dependencies import get_lobbies, Lobby


def get_current_admin(user = Depends(get_current_user)):
    if user != 'admin':
        raise HTTPException(401, "Not an admin")
    return user


router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/logs/{lobby_name}")
def get_game_logs(lobby_name, lobbies: dict[str, Lobby] = Depends(get_lobbies)):
    lobby = lobbies.get(lobby_name, None)
    if not lobby:
        raise HTTPException(404, "Lobby does not exists")
    return [[lobby.players[chair].name, message] for chair, message in lobby.game.logs]


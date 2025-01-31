# TODO: Structure file with all routes together and all models together and so on.
# TODO: Have a player be replaced by an AI if they don't join back on time
import logging

from fastapi import APIRouter, Depends

from server.auth import get_current_user

from .schemas import LobbyCreate, LobbyResponse
from .dependencies import Lobbies, HumanConnection


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('', response_model=list[LobbyResponse])
def get_lobbies(
        user: str = Depends(get_current_user),
        lobbies_crud: Lobbies = Depends(),
):
    # TODO: Move sorted to dependency
    return sorted(lobbies_crud.get_lobbies(), key=lambda lobby: lobby['creator'] != user)


@router.post('', response_model=LobbyResponse)
def create_lobby_route(
        lobby: LobbyCreate,
        user: str = Depends(get_current_user),
        lobbies_crud: Lobbies = Depends(),
):
    new_lobby = lobbies_crud.create_lobby(lobby, user)
    return new_lobby


@router.delete('/{id}', response_model=LobbyResponse)
def delete_lobby(
        lobby_name: str,
        user: str = Depends(get_current_user),
        lobbies_crud: Lobbies = Depends(),
):
    return lobbies_crud.delete_lobby(lobby_name, user)


@router.websocket("/connect")
async def connect_to_lobby(
        lobby_id: str,
        connection: HumanConnection = Depends(),
        lobbies_crud: Lobbies = Depends(),
):
    await lobbies_crud.connect_to_lobby(lobby_id, connection)

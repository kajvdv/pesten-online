# TODO: Structure file with all routes together and all models together and so on.
# TODO: Have a player be replaced by an AI if they don't join back on time
import logging

from fastapi import APIRouter, Depends, Form

from server.auth import get_current_user

from .schemas import LobbyCreate, LobbyResponse
from .dependencies import Lobbies, Connector, HumanConnection


logger = logging.getLogger(__name__)
router = APIRouter()

# The routes need to be async to make sure that everything is on the same thread

@router.get('', response_model=list[LobbyResponse])
async def get_lobbies(lobbies_crud: Lobbies = Depends()):
    return lobbies_crud.get_lobbies()


@router.post('', response_model=LobbyResponse)
async def create_lobby_route(
        lobby: LobbyCreate = Form(),
        lobbies_crud: Lobbies = Depends(),
):
    new_lobby = lobbies_crud.create_lobby(lobby)
    return new_lobby


@router.delete('/{id}', response_model=LobbyResponse)
async def delete_lobby(
        id: str,
        lobbies_crud: Lobbies = Depends(),
):
    return lobbies_crud.delete_lobby(id)


@router.websocket("/connect")
async def connect_to_lobby(
        lobby_id: str,
        connection: HumanConnection = Depends(),
        connector: Connector = Depends(),
):
    await connector.connect_to_lobby(lobby_id, connection)

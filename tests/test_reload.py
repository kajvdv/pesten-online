from pathlib import Path
import asyncio
import os

import pytest

from pesten.pesten import Pesten
from server.lobby.dependencies import Lobbies, create_game, construct_rules
from server.lobby import Lobby
from server.lobby.routes import create_lobby_route
from server.lobby.schemas import LobbyCreate


pickle_path = Path("tests/pickled_lobby.pickle")


@pytest.mark.asyncio
async def test_reload_lobbies(tmp_path):
    os.environ["LOBBIES_DIR"] = str(tmp_path)
    from server.reload import save_lobbies, load_lobbies
    # game = Pesten(2, 1, [0, 0, 0, 0, 0, 0, 0, 0])
    lobbies = {}
    lobbies_create_parameters = {}
    lobbies_crud = Lobbies('admin', lobbies)
    lobby_create = LobbyCreate(
        name='test_lobby',
        size=2,
        aiCount=1
    )

    await create_lobby_route(
        lobby_create,
        lobbies_crud,
        create_game(lobby_create, construct_rules(lobby_create)),
        'admin',
        lobbies_create_parameters
    )
    assert lobbies_create_parameters

    # lobby = await lobbies_crud.create_lobby('test_lobby', 1, game)
    lobby: Lobby = lobbies['test_lobby']
    for p in lobby.players:
        await p.connection.close()
    await asyncio.sleep(0)
    await lobby.play_choose(lobby.players[0], -1)
    assert len(lobbies['test_lobby'].players) == 2
    assert lobby.chooses == [-1]
    save_lobbies(lobbies, lobbies_create_parameters)
    lobbies = {}
    await load_lobbies(lobbies, lobbies_create_parameters)
    lobby = lobbies['test_lobby']
    for p in lobby.players:
        await p.connection.close()
    await asyncio.sleep(0)
    assert len(lobbies) == 1
    assert len(lobbies_create_parameters) == 1
    assert len(lobby.players) == 2
    assert lobby.chooses == [-1]

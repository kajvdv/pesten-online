from pathlib import Path
import asyncio
import os

import pytest

from pesten.pesten import Pesten
from server.lobby.dependencies import Lobbies, tasks


pickle_path = Path("tests/pickled_lobby.pickle")


@pytest.mark.asyncio
async def test_reload_lobbies(tmp_path):
    os.environ["LOBBIES_DIR"] = str(tmp_path)
    from server.reload import save_lobbies, load_lobbies
    game = Pesten(2, 1, [0, 0, 0, 0, 0, 0, 0, 0])
    lobbies = {}
    lobbies_crud = Lobbies('admin', lobbies)
    lobby = await lobbies_crud.create_lobby('test_lobby', 1, game)
    for p in lobby.players:
        await p.connection.close()
    await asyncio.sleep(0)
    assert len(lobbies['test_lobby'].players) == 2
    save_lobbies(lobbies)
    lobbies = {}
    await load_lobbies(lobbies)
    lobby = lobbies['test_lobby']
    for p in lobby.players:
        await p.connection.close()
    await asyncio.sleep(0)
    assert len(lobbies) == 1
    assert len(lobby.players) == 2

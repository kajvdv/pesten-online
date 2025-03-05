from pathlib import Path
import asyncio
import pickle
import os

import pytest

from server.lobby import Lobby
from server.lobby.lobby import AIConnection
from server.lobby.dependencies import Lobbies
from pesten.pesten import Pesten, card


pickle_path = Path("tests/pickled_lobby.pickle")


@pytest.mark.asyncio
async def test_reload_lobbies(tmp_path):
    os.environ["LOBBIES_DIR"] = str(tmp_path)
    from server.reload import save_lobbies, load_lobbies
    game = Pesten(2, 1, [0, 0, 0, 0, 0, 0, 0, 0])
    lobbies = {}
    lobbies_crud = Lobbies('admin', lobbies)
    lobby = await lobbies_crud.create_lobby('test_lobby', 1, game)
    save_lobbies(lobbies)
    lobbies = {}
    await load_lobbies(lobbies)
    assert len(lobbies) == 1

async def main():
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    game = Pesten(6, 8, cards, {
        0: 'draw_card-3',
        1: 'draw_card-3',
        2: 'draw_card-3',
        3: 'draw_card-3',
        4: 'draw_card-3',
        5: 'draw_card-3',
        6: 'draw_card-3',
        7: 'draw_card-3',
        8: 'draw_card-3',
        9: 'draw_card-3',
        10: 'draw_card-3',
        11: 'draw_card-3',
        12: 'draw_card-3',
    })
    lobbies = {}
    lobbies_crud = Lobbies('admin', lobbies)
    lobby = await lobbies_crud.create_lobby('test_lobby', 5, game)
    ai_count = len([player.connection for player in lobby.players if type(player.connection) == AIConnection])
    dump = pickle.dumps()
    # with open(pickle_path, 'wb') as file:
    #     pickle.dump([lobby, ai_count], file)

if __name__ == "__main__":
    asyncio.run(main())
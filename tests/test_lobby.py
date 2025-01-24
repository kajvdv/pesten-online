import json
import logging
import asyncio

import pytest

from fastapi.testclient import TestClient

from server.lobby import Lobbies, Game, Connection
from pesten.pesten import Pesten, card

logger = logging.getLogger(__name__)


class MockConnection:
    def __init__(self, username):
        self.username = username
        self.can_play = True
    
    async def accept(self):
        logger.info("Accepted mock connection")

    async def close(self):
        logger.info("Closing mock connection")

    async def send_json(self, data):
        if "error" in data:
            self.can_play = False
        else:
            self.can_play = True
        logger.info(f"{self.username} received {json.dumps(data, indent=2)}")

    async def receive_text(self):
        if not self.can_play:
            await asyncio.sleep(1)
        logger.info(f"{self.username} plays 1")
        return "1"

class OneLobby(Lobbies):    
    # Inits CRUD interface with a test game
    def __init__(self):
        super().__init__()
        game = Pesten(2, 1, [
            card(0, 0),
            card(0, 0),
            card(0, 0),
            card(0, 0),
        ])
        self.lobbies = {'test game': Game(game, 'player_1')}


def test_crud_lobbies():
    from server.lobby import Lobbies, LobbyCreate, LobbyResponse
    lobbies = Lobbies()
    lobby_name = 'test'
    lobby_create = LobbyCreate(name=lobby_name, size=2)
    lobbies.create_lobby(lobby_create, 'testuser')
    assert len(lobbies.get_lobbies()) == 1
    lobbies.delete_lobby(lobby_name, 'testuser')
    assert len(lobbies.get_lobbies()) == 0


def test_lobby_endpoints(client: TestClient):
    response = client.post("/lobbies", json={'name': 'test', 'size': 2})
    assert response.status_code < 400, response.text
    response = client.get('/lobbies')
    assert response.status_code < 400, response.text
    print(response.json())
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_playing_game(client: TestClient):
    lobbies_crud = OneLobby()
    player_1 = MockConnection('player_1')
    player_2 = MockConnection('player_2')
    lobby_name = "test game"
    await asyncio.gather(
        lobbies_crud.connect_to_lobby(lobby_name, player_2),
        lobbies_crud.connect_to_lobby(lobby_name, player_1),
    )
    assert lobbies_crud.lobbies[lobby_name].game.has_won == True
    assert lobbies_crud.lobbies[lobby_name].game.current_player == 0 # first player (player_1)


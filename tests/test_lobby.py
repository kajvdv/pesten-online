import json
import logging
import asyncio

import pytest

from fastapi.testclient import TestClient

from server.lobby import Lobbies, Game, Connection, ConnectionDisconnect
from pesten.pesten import Pesten, card

logger = logging.getLogger(__name__)


class MockConnection:
    def __init__(self, username):
        self.username = username
        self.closed = False
        self.can_play = True
        self.receive_count = 1
    
    async def accept(self):
        logger.info("Accepted mock connection")

    async def close(self):
        if self.closed:
            raise ConnectionDisconnect("Connection already closed")
        logger.info(f"Closing mock connection of {self.username}")
        self.closed = True

    async def send_json(self, data):
        if self.closed:
            raise ConnectionDisconnect("Connection was closed")
        if "error" in data:
            self.can_play = False
        else:
            self.can_play = True
        logger.info(f"{self.username} received {json.dumps(data, indent=2)}")

    async def receive_text(self):
        if self.closed:
            raise ConnectionDisconnect("Connection was closed")
        if not self.can_play:
            await asyncio.sleep(1 * self.receive_count)
        self.receive_count += 1
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
async def test_playing_game():
    lobbies_crud = OneLobby()
    player_1 = MockConnection('player_1')
    player_2 = MockConnection('player_2')
    lobby_name = "test game"
    assert len(lobbies_crud.lobbies[lobby_name].connections) == 0
    p2_connect_task = asyncio.create_task(lobbies_crud.connect_to_lobby(lobby_name, player_1))
    await asyncio.sleep(2)
    p1_connect_task = asyncio.create_task(lobbies_crud.connect_to_lobby(lobby_name, player_2))
    await asyncio.sleep(2)
    await p1_connect_task
    await p2_connect_task
    assert lobbies_crud.lobbies[lobby_name].game.has_won == True
    assert lobbies_crud.lobbies[lobby_name].game.current_player == 0 # first player (player_1)


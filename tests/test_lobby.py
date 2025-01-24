from fastapi.testclient import TestClient

from server.lobby import Lobbies, Game
from pesten.pesten import Pesten, card


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
        self.lobbies = {'test game': Game(game, 'admin')}


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


def test_playing_game(client: TestClient):
    client.app.dependency_overrides[Lobbies] = OneLobby
    response = client.get('/lobbies')
    assert response.status_code < 400, response.text
    assert len(response.json()) == 1


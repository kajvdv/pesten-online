

def test_crud_lobbies():
    from server.lobby import Lobbies, LobbyCreate, LobbyResponse
    lobbies = Lobbies()
    lobby_name = 'test'
    lobby_create = LobbyCreate(name=lobby_name, size=2)
    lobbies.create_lobby(lobby_create, 'testuser')
    assert len(lobbies.get_lobbies()) == 1
    lobbies.delete_lobby(lobby_name, 'testuser')
    assert len(lobbies.get_lobbies()) == 0


def test_lobby_endpoints(client):
    response = client.post("/lobbies", json={'name': 'test', 'size': 2})
    assert response.status_code < 400, response.text
    response = client.get('/lobbies')
    assert response.status_code < 400, response.text
    print(response.json())
    assert len(response.json()) == 1

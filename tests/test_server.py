from fastapi.testclient import TestClient

from server import app
from auth import get_current_user
from user import create_user

app.dependency_overrides[get_current_user] = lambda: None
client = TestClient(app)


def test_create_lobby():
    response = client.post('/lobbies', json={'size': 2})
    assert response.status_code == 200, response.text


def test_game_flow():
    create_user('kaj', '123')
    create_user('soy', '123')
    with (
        client.websocket_connect('lobbies/game?token=kaj&lobby_id=0') as connection_kaj,
        client.websocket_connect('lobbies/game?token=soy&lobby_id=0') as connection_soy,
    ):
        for _ in range(10):
            message = connection_kaj.receive_text()
            message = connection_soy.receive_text()
            connection_kaj.send_text('-1')
            message = connection_soy.receive_text()
            message = connection_kaj.receive_text()
            connection_soy.send_text('-1')
        message = connection_soy.receive_text()
        message = connection_kaj.receive_text()
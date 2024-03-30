from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def test_game_flow():
    with (
        client.websocket_connect('/?name=kaj') as connection_kaj,
        client.websocket_connect('/?name=soy') as connection_soy,
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
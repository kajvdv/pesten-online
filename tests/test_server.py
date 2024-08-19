import pytest
from sqlalchemy import select

from pesten.server import app
from pesten.auth import register_user, get_user, User
from pesten.lobby import LobbyCreate, create_lobby


def test_create_lobby(client):
    response = client.post('/lobbies', json={'size': 2})
    assert response.status_code == 200, response.text


def test_game_flow(client, db):
    register_user('kaj', '123', db)
    register_user('soy', '123', db)
    id = create_lobby(LobbyCreate(size=2), db.execute(select(User).where(User.username == 'kaj')).first()[0])
    connection_kaj = client.websocket_connect(f'lobbies/connect?name_override=kaj&lobby_id={id}')
    connection_soy = client.websocket_connect(f'lobbies/connect?name_override=soy&lobby_id={id}')
    with connection_kaj, connection_soy:
        connection_kaj.send_text('-1')
        message = connection_soy.receive_text()
        message = connection_kaj.receive_text()
        connection_kaj.send_text('-1')
        message = connection_soy.receive_text()
        message = connection_kaj.receive_text()
        connection_soy.send_text('-1')
        message = connection_soy.receive_text()
        message = connection_kaj.receive_text()


if __name__ == "__main__":
    pytest.main([__file__, '--asyncio-mode=auto'])
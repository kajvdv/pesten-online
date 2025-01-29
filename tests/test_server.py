from typing import Generator
import json 
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import time
import logging

import pytest
from sqlalchemy import select, create_engine, StaticPool
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from server.server import app
from pesten.pesten import Pesten, card
from server.database import get_db
from server.lobby import auth_websocket, Game


logger = logging.getLogger(__name__)
SECRET_KEY = os.environ['SECRET_KEY']


engine = create_engine(
    "sqlite://",
    connect_args={
        'check_same_thread': False
    },
    poolclass=StaticPool
)

def get_db_override():
    with Session(engine) as db:
        yield db


@pytest.fixture
def jwt_token_testuser1():
    token = jwt.encode(
        {"sub": "testuser1", 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=SECRET_KEY,
        algorithm="HS256"
    )
    return token


@pytest.fixture
def jwt_token_testuser2():
    token = jwt.encode(
        {"sub": "testuser2", 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=SECRET_KEY,
        algorithm="HS256"
    )
    return token


@pytest.fixture
def client(jwt_token_testuser1):
    from server.database import Base
    app.dependency_overrides[get_db] = get_db_override
    test_client = TestClient(app)
    test_client.headers['Authorization'] = f"Bearer {jwt_token_testuser1}"
    Base.metadata.create_all(engine)
    with test_client:
        yield test_client
    Base.metadata.drop_all(engine)


def test_auth(client):
    client.headers['Authorization'] = ""
    response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
    assert response.status_code == 400 # Does not exists

    response = client.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
    assert response.status_code == 204 # Register

    response = client.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
    assert response.status_code == 400 # Already exists

    response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': 'wrong'})
    assert response.status_code == 400 # Login with wrong password

    response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
    assert response.status_code == 200 # Succesful login

    access_token = response.json()
    response = client.get("http://localhost:8000/users/me", headers={"Authorization": "Bearer" + " " + access_token['access_token']})
    assert response.json() == "kaj" # Getting the username based of token


def test_create_and_join_game(
        client: TestClient,
        jwt_token_testuser1: str,
        jwt_token_testuser2: str
):
    response = client.get("/lobbies")
    assert response.status_code < 300, response.text
    response = client.post("/lobbies", json={"name": "test_lobby", "size": 2})
    assert response.status_code < 300, response.text
    response = client.get("/lobbies")
    assert response.status_code < 300, response.text
    assert len(response.json()) == 1
    lobby_id = response.json()[0]['id']
    
    connections = [
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}'),
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser2}')
    ]
    with connections[0], connections[1]:
        ...


def test_playing_simple_game(
        client: TestClient,
        jwt_token_testuser1: str,
        jwt_token_testuser2: str
):
    import server.lobby
    game = Pesten(2, 1, [
        # card(suit, value) for suit in range(4) for value in range(13)
        card(0, 0),
        card(0, 0),
        card(0, 0),
        card(0, 0),
    ])
    lobby_id = 'testlobby'
    server.lobby.lobbies = {lobby_id: Game(game, 'testuser1')}
    response = client.get('/lobbies')
    logger.info(f"Response was {json.dumps(response.json(), indent=2)}")
    
    connections = [
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}'),
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser2}')
    ]
    with connections[0], connections[1]:
        board = connections[0].receive_json()
        board = connections[1].receive_json()
        board = connections[0].receive_json()
        logger.debug(f"Board was {json.dumps(board, indent=2)}")
        connections[0].send_text('1')
        



def test_game_flow():
    app.dependency_overrides[auth_websocket] = lambda name_override: name_override
    pesten = Pesten(2, 8, [card(suit, value) for suit in range(4) for value in range(13)])
    game = Game(pesten, '1')
    app.dependency_overrides[get_lobby] = lambda: game
    client = TestClient(app)

    connection_1 = client.websocket_connect(f'lobbies/connect?name_override=1')
    connection_2 = client.websocket_connect(f'lobbies/connect?name_override=2')
    current_connection = connection_1

    def receive_message(current_connection):
        current_connection.send_text("1")
        message = connection_1.receive_text()
        print(message)
        message = connection_2.receive_text()
        print(message)
        if current_connection == connection_1:
            return connection_2
        else:
            return connection_1

    with connection_1, connection_2:
        message = connection_1.receive_text()
        print(message)
        assert len(json.loads(message)['otherPlayers']) == 1
        message = connection_1.receive_text()
        print(message)
        assert len(json.loads(message)['otherPlayers']) == 2
        message = connection_2.receive_text()
        print(message)
        assert len(json.loads(message)['otherPlayers']) == 2


        # test that 2 cannot play
        connection_2.send_text("0")
        assert len(json.loads(message)['otherPlayers']) == 2
        message = connection_2.receive_text()
        print(message)
        assert "Not your turn" in message
    
        # Test 1 can draw
        print(game.game.current_player)
        print(game.game.hands)
        connection_1.send_text("0")
        message = connection_1.receive_text()
        print(game.game.hands)
        message = connection_2.receive_text()
        print(message)

        # Test 2 can draw
        print(game.game.current_player)
        print(game.game.hands)
        connection_2.send_text("0")
        message = connection_2.receive_text()
        print(game.game.hands)
        message = connection_1.receive_text()
        print(message)

        for _ in range(9):
            current_connection = receive_message(current_connection)

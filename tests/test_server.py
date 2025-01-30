from typing import Generator
import asyncio
import json 
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import time
import os
import logging

import pytest
from sqlalchemy import select, create_engine, StaticPool
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from server.server import app
from pesten.pesten import Pesten, card
from server.database import get_db
from server.lobby import auth_websocket, Lobby, WebSocketDisconnect
from mocks import MockConnection


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


@pytest.fixture
def init_lobby():
    import server.lobby
    lobby_id = 'testlobby'
    pesten = Pesten(2, 1, [
        card(0, 0),
        card(0, 0),
        card(0, 0),
        card(0, 0),
    ])
    lobby = Lobby(pesten, 'testuser1')
    server.lobby.lobbies = {lobby_id: lobby}
    yield lobby
    from importlib import reload
    reload(server.lobby)


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


# @pytest.mark.asyncio
# async def test_playing_game(init_lobby):
#     # This test is nice because it didn't need auth, but that is kind of resolved now.
#     from server.lobby import Lobbies
#     lobbies_crud = Lobbies()
#     player_1 = MockConnection('testuser1')
#     player_2 = MockConnection('testuser2')
#     lobby_name = "testlobby"
#     assert len(init_lobby.players) == 0
#     p2_connect_task = asyncio.create_task(lobbies_crud.connect_to_lobby(lobby_name, player_1))
#     # await asyncio.sleep(3)
#     p1_connect_task = asyncio.create_task(lobbies_crud.connect_to_lobby(lobby_name, player_2))
#     # await asyncio.sleep(3)
#     await p1_connect_task
#     await p2_connect_task
#     assert init_lobby.game.has_won == True
#     assert init_lobby.game.current_player == 0 # first player (player_1)


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
        jwt_token_testuser2: str,
        init_lobby
):
    lobby_id = 'testlobby'
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
    assert init_lobby.game.has_won
    assert init_lobby.game.current_player == 0


def test_create_simple_two_ai_game(
        client: TestClient,
        jwt_token_testuser1: str
):
    response = client.get("/lobbies")
    assert response.status_code < 300, response.text
    response = client.post("/lobbies", json={"name": "test_lobby", "size": 3, 'aiCount': 2})
    assert response.status_code < 300, response.text
    response = client.get("/lobbies")
    assert response.status_code < 300, response.text
    assert len(response.json()) == 1
    lobby_id = response.json()[0]['id']
    
    connection = client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}')
    with connection:
        ...


def test_play_game_against_ai(
        client: TestClient,
        jwt_token_testuser1: str
):
    lobby_id = 'test_lobby'
    response = client.post("/lobbies", json={"name": lobby_id, "size": 2, 'aiCount': 1})
    assert response.status_code < 300, response.text
    
    connection = client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}')
    with connection:
        board = connection.receive_json()
        connection.send_text("1")
        board = connection.receive_json()
        assert board['message']

    
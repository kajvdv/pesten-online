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
from server.lobby.lobby import Lobby
from server.lobby.dependencies import GameFactory


logger = logging.getLogger(__name__)
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


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


class GameFactoryOverride(GameFactory):
    def create_game(self, size, rules, joker_count, user):
        game = Pesten(2, 1, [
            card(0, 0),
            card(0, 0),
            card(0, 0),
            card(0, 0),
        ])
        return Lobby(game, user)


@pytest.fixture
def jwt_token_testuser1():
    token = jwt.encode(
        {"sub": "testuser1", 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=ACCESS_TOKEN_SECRET,
        algorithm="HS256"
    )
    return token


@pytest.fixture
def jwt_token_testuser2():
    token = jwt.encode(
        {"sub": "testuser2", 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=ACCESS_TOKEN_SECRET,
        algorithm="HS256"
    )
    return token


@pytest.fixture
def client(jwt_token_testuser1):
    from server.database import Base
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = get_db_override
    test_client = TestClient(app)
    test_client.headers['Authorization'] = f"Bearer {jwt_token_testuser1}"
    Base.metadata.create_all(engine)
    with test_client:
        yield test_client
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def reload():
    from importlib import reload
    import server.lobby.dependencies
    logger.debug(f"Reloading dependencies module to reset lobbies")
    reload(server.lobby.dependencies)
    assert len(server.lobby.dependencies.lobbies) == 0


@pytest.fixture
def init_lobby():
    import server.lobby.dependencies
    lobby_id = 'testlobby'
    pesten = Pesten(2, 1, [
        card(0, 0),
        card(0, 0),
        card(0, 0),
        card(0, 0),
    ])
    lobby = Lobby(pesten, 'testuser1')
    server.lobby.dependencies.lobbies = {lobby_id: lobby}
    return (lobby_id, lobby)


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
    response = client.post("/lobbies", data={"name": "test_lobby", "size": 2})
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
    lobby_id, lobby = init_lobby 
    connections = [
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}'),
        client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser2}')
    ]
    with connections[0], connections[1]:
        board = connections[0].receive_json()
        board = connections[1].receive_json()
        board = connections[0].receive_json()
        logger.debug(f"Board was {json.dumps(board, indent=2)}")
        connections[0].send_text('0')
    assert lobby.game.has_won
    assert lobby.game.current_player == 0


def test_create_simple_two_ai_game(
        client: TestClient,
        jwt_token_testuser1: str
):
    response = client.get("/lobbies")
    assert response.status_code < 300, response.text
    response = client.post("/lobbies", data={"name": "test_lobby", "size": 3, 'aiCount': 2})
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
    client.app.dependency_overrides[GameFactory] = GameFactoryOverride
    lobby_id = "testlobby"
    response = client.post("/lobbies", data={"name": lobby_id, "size": 2, 'aiCount': 1})
    assert response.status_code < 300
    
    connection = client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}')
    with connection:
        board = connection.receive_json()
        connection.send_text("0")
        board = connection.receive_json()
        assert board['message']


class ErrorAIOverride(GameFactoryOverride):
    def create_game(self, size, rules, joker_count, user):
        return Lobby(Pesten(2, 1, [0, 0, 0, 14]), user)

def test_ai_throws_error(
        client: TestClient,
        jwt_token_testuser1
):
    client.app.dependency_overrides[GameFactory] = ErrorAIOverride
    lobby_id = "testlobby"
    response = client.post("/lobbies", data={"name": lobby_id, "size": 2, 'aiCount': 1})
    assert response.status_code < 300

    connection = client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}&token={jwt_token_testuser1}')
    with connection:
        board = connection.receive_json()
        connection.send_text("-1")
        board = connection.receive_json()
        logger.info(board)
    

def test_get_rules(client: TestClient):
    lobby_id = "testlobby"
    response = client.post("/lobbies", data={"name": lobby_id, "size": 2, 'aiCount': 1, 'jack': "testRule"})
    assert response.status_code < 300, response.text

    response = client.get(f"lobbies/{lobby_id}/rules")
    assert response.status_code < 300
    assert response.json()['jack'] == 'testRule'

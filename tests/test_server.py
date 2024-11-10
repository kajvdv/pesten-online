import json 
import time

import pytest
from sqlalchemy import select, create_engine, StaticPool
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from pesten.server import app
from pesten.pesten import Pesten, card
from pesten.database import get_db
from pesten.auth import register_user, get_user, User, get_current_user
from pesten.lobby import LobbyCreate, create_lobby, auth_websocket, get_lobby, Game


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


def test_create_and_join_game():
    app.dependency_overrides[get_current_user] = lambda: "admin"
    app.dependency_overrides[auth_websocket] = lambda: "admin"
    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)

    response = client.get("/lobbies")
    response = client.post("/lobbies", json={"size": 2})
    response = client.get("/lobbies")
    assert len(response.json()) == 1
    lobby_id = response.json()[0]['id']

    connection = client.websocket_connect(f'/lobbies/connect?lobby_id={lobby_id}')
    with connection:
        ...


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

if __name__ == "__main__":
    test_create_and_join_game()

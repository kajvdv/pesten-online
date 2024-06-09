"""
This is some auxillary code for developing the game server
Start the server using `uvicorn client:app`
Start two clients each in a seperate terminal with `python -m client {name}`
Choose name whatever you like
No need for tokens!
"""

import json
from threading import Thread

import requests
from websockets.sync.client import connect

import sys
from server import app
from auth import get_current_user
from lobby import Lobby
import lobby


def get_current_user_override(token: str):
    print("Get token override for", token)
    return token

app.dependency_overrides[get_current_user] = get_current_user_override
lobby.lobbies = [Lobby(2), Lobby(2)]


def client(name):
    lobbies = requests.get("http://localhost:8000/lobbies")
    lobbies = lobbies.json()
    print("lobbies")
    for index, lobby in enumerate(lobbies):
        print(f"{index}. {lobby['size']}/{lobby['capacity']}")
    # lobby_id = input("Welke lobby wil je joinen?: ")
    lobby_id = "0"
    with connect(f'ws://localhost:8000/lobbies/connect?token={name}&lobby_id={lobby_id}') as connection:
        def receive():
            while True:
                data = connection.recv()
                board = json.loads(data)
                if "error" in board:
                    print(board['error'])
                    continue
                print(f"Topcard is {board['topcard']}")
                if board["current_player"] == name:
                    print("It's your turn")
                    print("\n".join([str(card_id) + ": " + card['suit'] + " " + card['value'] for card_id, card in enumerate(board["hand"], start=1)]))
        
        receive_thread = Thread(target=receive)
        receive_thread.start()
        print("Started receiving messages")
        while True:
            message = input() # Client can make a choose
            connection.send(message) # Choose is send to the backend


if __name__ == "__main__":
    client(sys.argv[1])
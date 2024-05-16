import time
from multiprocessing import Process
from threading import Thread
import subprocess
import asyncio
import requests
from websockets.sync.client import connect


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

from pesten import Pesten, card, card_string, CannotDraw


class Lobby:
    def __init__(self, capacity) -> None:
        self.game = Pesten(capacity, 8, [card(suit, value) for suit in range(4) for value in range(13)])
        self.started = False
        self.connections: list[WebSocket] = [] # What if player disconnects?
        self.capacity = capacity

lobbies = [Lobby(2), Lobby(4)]

app = FastAPI()

@app.get('/')
def get_lobbies():
    return [{'size': len(lobby.connections), 'capacity': lobby.capacity} for lobby in lobbies]

@app.websocket("/ws")
async def connect_to_lobby(websocket: WebSocket, lobby_id: int = 0):
    lobby = lobbies[lobby_id]
    await websocket.accept()
    player_id = len(lobby.connections)
    lobby.connections.append(websocket)
    if len(lobby.connections) == lobby.capacity:
        lobby.started = True
    try:
        await websocket.send_text(f"Topcard is {card_string(lobby.game.play_stack[-1])}")
        hand = "\n".join([str(index) + ": " + card_string(card) for index, card in enumerate(lobby.game.hands[player_id], start=1)])
        await websocket.send_text(hand)
        while True:
            data = await websocket.receive_text()
            if not lobby.started:
                continue
            if lobby.game.current_player != lobby.connections.index(websocket):
                await websocket.send_text("Not your turn")
                continue
            print(f"{lobby_id} received from client {lobby.connections.index(websocket)} {data}")
            try:
                next_player = lobby.game.play_turn(int(data))
            except ValueError:
                await websocket.send_text("Invalid choose")
                continue
            for conn in lobby.connections:
                await conn.send_text(f"Topcard is {card_string(lobby.game.play_stack[-1])}")
            hand = "\n".join([str(index) + ": " + card_string(card) for index, card in enumerate(lobby.game.hands[next_player], start=1)])
            await lobby.connections[next_player].send_text(hand)
    except WebSocketDisconnect:
        print(f"websocket with id {lobby_id} disconnected")


def client():
    lobbies = requests.get("http://localhost:8000/")
    lobbies = lobbies.json()
    print("lobbies")
    for index, lobby in enumerate(lobbies):
        print(f"{index}. {lobby['size']}/{lobby['capacity']}")
    lobby_id = input("Welke lobby wil je joinen?: ")
    with connect(f'ws://localhost:8000/ws?lobby_id={lobby_id}') as connection:
        start_message = connection.recv()
        print(start_message)

        def receive():
            while True:
                hand = connection.recv() # Server unblocks client by sending the hand of the relevant player
                print(hand)
        
        receive_thread = Thread(target=receive)
        receive_thread.start()
        print("Started receiving messages")
        while True:
            message = input() # Client can make a choose
            connection.send(message) # Choose is send to the backend





if __name__ == "__main__":
    # Start the server with "uvicorn lobby_new:app"
    client()
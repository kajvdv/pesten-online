import time
from multiprocessing import Process
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
    lobby.connections.append(websocket)
    if len(lobby.connections) == lobby.capacity:
        for conn in lobby.connections:
            await conn.send_text(f"Lobby is full, Topcard is {card_string(lobby.game.play_stack[-1])}")
    try:
        while True:
            data = await websocket.receive_text()
            if lobby.game.current_player != lobby.connections.index(websocket):
                await websocket.send_text("Not your turn")
                continue
            print(f"{lobby_id} received from client {lobby.connections.index(websocket)} {data}")
            lobby.game.play_turn(int(data))
            for conn in lobby.connections:
                await conn.send_text(f"Topcard is {card_string(lobby.game.play_stack[-1])}")
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
        first_message = connection.recv()
        print("First message from server:", first_message)
        while True:
            message = input()
            connection.send(message)
            try:
                data = connection.recv(1)
                print("New message from server:", data)
            except Exception as e:
                print(e)

if __name__ == "__main__":
    # Start the server with "uvicorn lobby_new:app"
    client()
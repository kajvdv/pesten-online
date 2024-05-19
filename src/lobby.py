import sys
import json
import random
from multiprocessing import Process
from threading import Thread
import requests
from websockets.sync.client import connect

from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pesten import Pesten, card, card_string, CannotDraw
from auth import decode_token


class Card(BaseModel):
    suit: str
    value: str

    def __init__(self, card):
        suit, value = card_string(card).split(' ')
        super().__init__(suit=suit, value=value)


class Board(BaseModel):
    topcard: Card
    can_draw: bool
    current_player: str
    hand: list[Card]


class Lobby:
    def __init__(self, capacity) -> None:
        self.game = Pesten(capacity, 8, [card(suit, value) for suit in range(4) for value in range(13)])
        self.started = False
        self.connections: dict[str, WebSocket] = {}
        self.names = []
        self.capacity = capacity


    async def add_connection(self, name, websocket: WebSocket):
        if name in self.names:
            print("rejoining", name)
        elif self.started:
            raise Exception("Lobby is full")
        elif name in self.names:
            raise Exception("Player already in lobby")
        else:
            self.names.append(name)
        self.connections[name] = websocket
        if len(self.names) == self.capacity:
            self.started = True
        await self.update_boards()
    

    async def send_hand(self, name):
        player_id = self.names.index(name)
        hand = "\n".join([
            str(index) + ": " + card_string(card)
            for index, card in enumerate(self.game.hands[player_id], start=1)
        ])
        websocket = self.connections[name]
        await websocket.send_text(hand)


    async def update_boards(self):
        for name, conn in self.connections.items():
            player_id = self.names.index(name)
            board = Board(
                topcard=Card(self.game.play_stack[-1]),
                can_draw=bool(self.game.draw_stack),
                current_player=self.names[self.game.current_player],
                hand=[Card(card) for card in self.game.hands[player_id]]
            )
            await conn.send_json(board.model_dump())


    async def get_choose(self, name):
        websocket: WebSocket = self.connections[name]
        choose = await websocket.receive_text()
        print(f"New message from {name} in lobby {lobbies.index(self)}")
        if not self.started:
            await websocket.send_json({"error": "Game not started"})
            return
        if self.game.current_player != self.names.index(name):
            await websocket.send_json({"error": "Not your turn"})
            return
        
        try:
            choose = int(choose)
        except ValueError:
            await websocket.send_json({"error": "Invalid choose"})
            return
        self.game.play_turn(choose)
        await self.update_boards()




async def game_loop(websocket: WebSocket, name, lobby: Lobby):
    await lobby.add_connection(name, websocket)
    try:
        while True:
            await lobby.get_choose(name)
    except WebSocketDisconnect:
        print(f"websocket with id disconnected")
    except Exception as e:
        print("ERROR", e)
        websocket.close()
    finally:
        del lobby.connections[name]



lobbies = [Lobby(2), Lobby(2)]
router = APIRouter(prefix='/lobbies')

@router.get('')
def get_lobbies():
    return [{'size': len(lobby.connections), 'capacity': lobby.capacity} for lobby in lobbies]


@router.websocket("/connect")
async def connect_to_lobby(websocket: WebSocket, token: str, lobby_id: int = 0):
    data = decode_token(token)
    name = data['sub']
    lobby = lobbies[lobby_id]
    await websocket.accept()
    await game_loop(websocket, name, lobby)


def client(token):
    data = decode_token(token)
    name = data['sub']
    lobbies = requests.get("http://localhost:8000/lobbies")
    lobbies = lobbies.json()
    print("lobbies")
    for index, lobby in enumerate(lobbies):
        print(f"{index}. {lobby['size']}/{lobby['capacity']}")
    # lobby_id = input("Welke lobby wil je joinen?: ")
    lobby_id = "0"
    with connect(f'ws://localhost:8000/lobbies/connect?token={token}&lobby_id={lobby_id}') as connection:
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
    # Start the server with "uvicorn lobby_new:app"
    tokens = []
    client(tokens[int(sys.argv[1])])
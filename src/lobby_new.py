import json
from multiprocessing import Process
from threading import Thread
import requests
from websockets.sync.client import connect

from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from pesten import Pesten, card, card_string, CannotDraw


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
        self.connections: list[WebSocket] = [] # What if player disconnects?
        self.capacity = capacity


    async def add_connection(self, websocket: WebSocket):
        if self.started:
            raise Exception("Lobby is full")
        player_id = len(self.connections)
        self.connections.append(websocket)
        if len(self.connections) == self.capacity:
            self.started = True
        await websocket.send_text(str(player_id)) # First message send to the client
        await self.update_boards()
        return player_id
    

    async def send_hand(self, player_id):
        hand = "\n".join([
            str(index) + ": " + card_string(card)
            for index, card in enumerate(self.game.hands[player_id], start=1)
        ])
        websocket = self.connections[player_id]
        await websocket.send_text(hand)


    async def update_boards(self):
        for player_id, conn in enumerate(self.connections):
            board = Board(
                topcard=Card(self.game.play_stack[-1]),
                can_draw=bool(self.game.draw_stack),
                current_player=str(self.game.current_player),
                hand=[Card(card) for card in self.game.hands[player_id]]
            )
            await conn.send_json(board.model_dump())


    async def get_choose(self, player_id):
        websocket: WebSocket = self.connections[player_id]
        choose = await websocket.receive_text()
        print(f"New message from {player_id} in lobby {lobbies.index(self)}")
        if not self.started:
            await websocket.send_json({"error": "Game not started"})
            return
        if self.game.current_player != player_id:
            await websocket.send_json({"error": "Not your turn"})
            return
        
        try:
            choose = int(choose)
        except ValueError:
            await websocket.send_json({"error": "Invalid choose"})
            return
        self.game.play_turn(choose)
        await self.update_boards()




async def game_loop(websocket: WebSocket, lobby: Lobby):
    player_id = await lobby.add_connection(websocket)
    try:
        while True:
            await lobby.get_choose(player_id)
    except WebSocketDisconnect:
        print(f"websocket with id disconnected")




## Test code below, dont use in other modules



lobbies = [Lobby(2), Lobby(4)]
app = FastAPI()

@app.get('/')
def get_lobbies():
    return [{'size': len(lobby.connections), 'capacity': lobby.capacity} for lobby in lobbies]


@app.websocket("/ws")
async def connect_to_lobby(websocket: WebSocket, lobby_id: int = 0):
    lobby = lobbies[lobby_id]
    await websocket.accept()
    await game_loop(websocket, lobby)


def client():
    lobbies = requests.get("http://localhost:8000/")
    lobbies = lobbies.json()
    print("lobbies")
    for index, lobby in enumerate(lobbies):
        print(f"{index}. {lobby['size']}/{lobby['capacity']}")
    lobby_id = input("Welke lobby wil je joinen?: ")
    with connect(f'ws://localhost:8000/ws?lobby_id={lobby_id}') as connection:
        player_id = connection.recv()
        def receive():
            while True:
                data = connection.recv()
                board = json.loads(data)
                if "error" in board:
                    print(board['error'])
                    continue
                print(f"Topcard is {board['topcard']}")
                if board["current_player"] == player_id:
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
    client()
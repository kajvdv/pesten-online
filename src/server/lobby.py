import json
import random
import logging
import asyncio

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, status

from pesten.pesten import Pesten, card, card_string, CannotDraw
from server.auth import get_current_user, User, decode_token

logger = logging.getLogger(__name__)


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
    otherPlayers: dict[str, int]
    hand: list[Card]


class ConnectionDisconnect(Exception):
    ...


class Connection():
    def __init__(self, websocket: WebSocket, token: str):
        self.username = get_current_user(token)
        self.websocket = websocket

    async def accept(self):
        await self.websocket.accept()

    async def close(self):
        await self.websocket.close()

    async def send_json(self, data):
        try:
            await self.websocket.send_json(data)
        except WebSocketDisconnect as e:
            raise ConnectionDisconnect(e)

    async def receive_text(self) -> str:
        try:
            return await self.websocket.receive_text()
        except WebSocketDisconnect as e:
            raise ConnectionDisconnect(e)


class Game:
    def __init__(self, game: Pesten, creator) -> None:
        self.game = game
        self.started = False
        self.connections: dict[str, Connection] = {}
        self.names = [creator]
        self.capacity = game.player_count


    async def add_connection(self, name, connection: Connection):
        if name in self.names:
            logger.info(f"rejoining {name}")
        elif self.started:
            raise Exception("Lobby is full")
        elif name in self.names: #TODO: check if can be removed
            raise Exception("Player already in lobby")
        else:
            self.names.append(name)
        self.connections[name] = connection
        if len(self.names) == self.capacity:
            self.started = True
        await self.update_boards() #TODO: Add message that a player joined
    

    # async def send_hand(self, name):
    #     player_id = self.names.index(name)
    #     hand = "\n".join([
    #         str(index) + ": " + card_string(card)
    #         for index, card in enumerate(self.game.hands[player_id], start=1)
    #     ])
    #     connection = self.connections[name]
    #     await connection.send_text(hand)


    async def update_boards(self, message=""):
        logger.debug("Updating player's board")
        for name, conn in self.connections.items():
            player_id = self.names.index(name)
            board = Board(
                topcard=Card(self.game.play_stack[-1]),
                can_draw=bool(self.game.draw_stack),
                current_player=self.names[self.game.current_player],
                otherPlayers={name: len(self.game.hands[self.names.index(name)]) for name in self.names},
                hand=[Card(card) for card in self.game.hands[player_id]]
            )
            await conn.send_json({
                **board.model_dump(),
                'message': message
            })


    async def get_choose(self, name):
        connection: Connection = self.connections[name]
        choose = await connection.receive_text()
        # choose = 0
        # print(f"New message from {name} in lobby {list(lobbies.values()).index(self)}")
        if not self.started:
            await connection.send_json({"error": "Game not started"})
            return
        if self.game.current_player != self.names.index(name):
            await connection.send_json({"error": "Not your turn"})
            return
        
        try:
            choose = int(choose)
        except ValueError:
            await connection.send_json({"error": "Invalid choose"})
            return
        self.game.play_turn(choose)
        if self.game.has_won:
            logger.info(f"{name} has won the game!")
            await self.update_boards(f"{name} has won the game!")
            logger.debug(f"connection count {len(self.connections)}")
            for connection in self.connections:
                await asyncio.gather(*[conn.close() for conn in self.connections.values()])
        else:
            await self.update_boards(message="")


async def game_loop(websocket: Connection, name, lobby: Game):
    await lobby.add_connection(name, websocket)
    try:
        while not lobby.game.has_won:
            await lobby.get_choose(name)
    except ConnectionDisconnect as e:
        logger.error(f"websocket disconnected {e}")


class LobbyCreate(BaseModel):
    name: str
    size: int

# lobbies = {}
router = APIRouter()


def create_game(lobby: LobbyCreate, user: str = Depends(get_current_user)):
    size = lobby.size
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Pesten(size, 8, cards)
    new_game = Game(game, user)
    return new_game


lobbies: dict[str, Game] = {}
class Lobbies:
    # Defining CRUD operations. Keep clean of FastAPI stuff, or put in constructor
    #TODO Maybe put auth stuff also in here to relief endpoints

    def get_lobbies(self):
        return [{
        'id': id,
        'size': len(lobby.names),
        'capacity': lobby.capacity,
        'creator': lobby.names[0],
        'players': lobby.names,
    } for id, lobby in lobbies.items()]

    def get_lobby(self, lobby_name):
        return lobbies[lobby_name]

    def create_lobby(self, lobby_create: LobbyCreate, user):
        new_game = create_game(lobby_create, user)
        if lobby_create.name in lobbies:
            raise HTTPException(status_code=400, detail="Lobby name already exists")
        lobbies[lobby_create.name] = new_game
        print(f"Added new lobby with name {lobby_create.name}")
        print(f"Total lobbies now {len(lobbies)}")
        return {
            'id': lobby_create.name,
            'size': len(new_game.names),
            'capacity': new_game.capacity,
            'creator': user,
            'players': new_game.names,
        }

    def delete_lobby(self, lobby_name, user):
        try:
            lobby_to_be_deleted = lobbies[lobby_name]
        except KeyError as e:
            print(f'Lobby with name of {e} does not exist')
            raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
        if lobby_to_be_deleted.names[0] != user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you") # Contains FastAPI stuff
        print("deleting lobby")
        lobby = lobbies.pop(lobby_name)
        print("address lobby", lobby)
        to_be_returned = {
            'id': lobby_name,
            'size': len(lobby.names),
            'capacity': lobby.capacity,
            'creator': user,
            'players': lobby.names,
        }
        del lobby # Not sure if this is necessary
        return to_be_returned

    async def connect_to_lobby(self, lobby_name: str, connection: Connection):
        await connection.accept()
        try:
            lobby = lobbies[lobby_name]
        except KeyError as e:
            logger.error(f"Could not find {lobby_name} in lobbies")
            logger.error(f"Current lobbies: {lobbies}")
            return
        await game_loop(connection, connection.username, lobby)


class LobbyResponse(BaseModel):
    id: str
    size: int
    capacity: int
    creator: str
    players: list[str]


@router.get('', response_model=list[LobbyResponse])
def get_lobbies(
    user: str = Depends(get_current_user),
    lobbies_crud: Lobbies = Depends(),
):
    return sorted(lobbies_crud.get_lobbies(), key=lambda lobby: lobby['creator'] != user)


@router.post('', response_model=LobbyResponse)
def create_lobby_route(
    lobby: LobbyCreate,
    user: str = Depends(get_current_user),
    lobbies_crud: Lobbies = Depends(),
):
    new_lobby = lobbies_crud.create_lobby(lobby, user)
    return new_lobby

@router.delete('/{id}', response_model=LobbyResponse)
def delete_lobby(
    lobby_name: str,
    user: str = Depends(get_current_user),
    lobbies_crud: Lobbies = Depends(),
):
    return lobbies_crud.delete_lobby(lobby_name, user)


def auth_websocket(token: str):
    name = get_current_user(token)
    return name

# def get_lobby(lobby_id: str):
#     print(lobbies)
#     return lobbies[lobby_id]

def get_current_user_websocket(token: str): #TODO: Check if this can be removed
    return get_current_user(token)

@router.websocket("/connect")
async def connect_to_lobby(
    lobby_id: str,
    connection: Connection = Depends(),
    lobbies_crud: Lobbies = Depends(),
    # lobby = Depends(get_lobby),
    # name: str = Depends(auth_websocket)
):
    # lobby = lobbies_crud.get_lobby(lobby_id)
    # await game_loop(connection, connection.username, lobby)
    await lobbies_crud.connect_to_lobby(lobby_id, connection)



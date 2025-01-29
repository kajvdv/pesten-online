# TODO: Structure file with all routes together and all models together and so on.
# TODO: Have a player be replaced by an AI if they don't join back on time
import json
import random
import logging
import asyncio

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, status

from pesten.pesten import Pesten, card, card_string, CannotDraw
from pesten.agent import Agent
from server.auth import get_current_user, User, decode_token


logger = logging.getLogger(__name__)


class Card(BaseModel):
    suit: str
    value: str

    @classmethod
    def from_int(cls, card):
        suit, value = card_string(card).split(' ')
        return cls(suit=suit, value=value)


class Board(BaseModel):
    topcard: Card
    can_draw: bool
    current_player: str
    otherPlayers: dict[str, int]
    hand: list[Card]
    message: str


class ConnectionDisconnect(Exception):
    ...


class Connection():
    def __init__(self, websocket: WebSocket, token: str):
        self.username = get_current_user(token) # For authentication
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
        

class AIConnection(Connection):
    def __init__(self, game: Pesten, player_index):
        self.game = game
        self.agent = Agent(player_index)
        self.event = asyncio.Event()

    async def accept(self):
        ...
    
    async def close(self):
        self.event.set() # Unblock if it was waiting on the event
    
    async def send_json(self, data: dict):
        # This function can trigger the event when it detects that its this AI its turn
        logger.debug(f"Received for {self.agent.player_index} : \n{json.dumps(data, indent=2)}")
        if 'error' in data:
            return
        message = Board(**data)
        if self.game.current_player == self.agent.player_index:
            logger.debug(f"{self.agent.player_index}: Setting the event")
            self.event.set()
    
    async def receive_text(self) -> str:
        logger.debug(f"Waiting for event to be set on {self.agent.player_index}")
        await self.event.wait()
        logger.debug(f"{self.agent.player_index} generating choose")
        choose = self.agent.generate_choose(self.game)
        self.event.clear()
        return choose


class Player:
    # Structure holding player information 
    def __init__(self, name, connection: Connection):
        self.name = name
        self.connection = connection


class Lobby:
    """The game does not know who the players are.
    It only knows about 'chairs' and that the chairs are occupied somehow.
    The lobby makes sure that the players occupy the chairs and stay there.
    Players should not switch from chairs.
    The game expects the client code to have a list that represents the chairs.
    The current_player attribute is suppose to point at the chair of the current_player
    You can get the player by dereferecing the list with that attribute."""
    def __init__(self, game: Pesten, creator: str) -> None:
        self.creator = creator
        self.game = game
        self.started = False
        # self.connections: dict[str, Connection] = {}
        # self.names = [creator]
        self.capacity = game.player_count
        # self.agents = agents
        self.players: list[Player] = [] # List corresponds with players in pesten game


    async def connect(self, new_player: Player):
        connection = new_player.connection
        name = new_player.name
        # Creates a gameloop for a connection
        if player := self.get_player_by_name(name):
            # Close the existing loop
            logger.info(f"rejoining {name}")
            try:
                await player.connection.close()
            except:
                logger.error("Error while closing a connection of an already joined player")
            # player = new_player This instead of the things below?
            index = self.players.index(player)
            self.players[index] = new_player # Replacing the player object
        elif self.started:
            raise Exception("Lobby is full")
        else:
            logger.info(f"Adding player {new_player.name} to the lobby")
            self.players.append(new_player)
        if len(self.players) == self.capacity:
            self.started = True
        self.update_boards(message=f"{name} joined the game")
        try:
            while not self.game.has_won:
                choose = await connection.receive_text()
                logger.debug(f"{new_player.name} choose {choose}")
                self.play_choose(new_player, choose)
                logger.info(f"{new_player.name} successfully played a choose")
        except Exception as e:
            logger.error(f"Error in the connection: {e}")
        logger.info(f"{new_player.name} exited its gameloop")
                

    def update_boards(self, message=""):
        logger.debug("Updating player's board")
        for player_id, player in enumerate(self.players):
            board = Board(
                topcard=Card.from_int(self.game.play_stack[-1]),
                can_draw=bool(self.game.draw_stack),
                current_player=self.players[self.game.current_player].name,
                otherPlayers={player.name: len(self.game.hands[self.players.index(player)]) for player in self.players},
                hand=[Card.from_int(card) for card in self.game.hands[player_id]],
                message=message
            )
            asyncio.create_task(player.connection.send_json({**board.model_dump()}))

    
    def get_player_by_name(self, name: str) -> Player:
        try:
            player = next(filter(lambda p: p.name == name, self.players))
        except StopIteration as e:
            logger.info(f"Could not find {name} in the lobby")
            return None
        return player
        

    def play_choose(self, player: Player, choose):
        # player = self.get_player_by_name(name)
        name = player.name
        if not self.started:
            asyncio.create_task(player.connection.send_json({"error": "Game not started"}))
            return
        if self.game.current_player != self.players.index(player):
            asyncio.create_task(player.connection.send_json({"error": "Not your turn"}))
            return
        try:
            choose = int(choose)
        except ValueError:
            asyncio.create_task(player.connection.send_json({"error": "Invalid choose"}))
            return
        self.game.play_turn(choose)
        if self.game.has_won:
            logger.info(f"{name} has won the game!")
            self.update_boards(f"{name} has won the game!")
            connections = map(lambda player: player.connection, self.players)
            asyncio.gather(*[conn.close() for conn in connections])
        else:
            self.update_boards(message="")


class LobbyCreate(BaseModel):
    name: str
    size: int

router = APIRouter()


def create_game(lobby: LobbyCreate, user: str = Depends(get_current_user)) -> Lobby:
    size = lobby.size
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Pesten(size, 8, cards)
    new_game = Lobby(game, user)
    return new_game


lobbies: dict[str, Lobby] = {}
class Lobbies:
    # Defining CRUD operations. Keep clean of FastAPI stuff, or put in constructor
    #TODO Maybe put auth stuff also in here, so 'user' can be removed from endpoints

    def get_lobbies(self):
        return [{
            'id': id,
            'size': len(lobby.players),
            'capacity': lobby.capacity,
            'creator': lobby.creator,
            'players': list(map(lambda p: p.name, lobby.players)),
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
            'size': len(new_game.players),
            'capacity': new_game.capacity,
            'creator': user,
            'players': list(map(lambda p: p.name, new_game.players)),
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
        # await game_loop(connection, connection.username, lobby)
        await lobby.connect(Player(connection.username, connection))


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



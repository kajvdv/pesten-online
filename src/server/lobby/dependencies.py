from typing import Protocol
import asyncio
import logging
import json
import random

from fastapi import Depends, BackgroundTasks, status
from fastapi.exceptions import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from server.auth import get_current_user
from pesten.pesten import Pesten, card

from .schemas import LobbyCreate
from .lobby import Lobby, NullConnection, AIConnection, Player, ConnectionDisconnect


logger = logging.getLogger(__name__)


# def create_game(lobby: LobbyCreate, user: str = Depends(get_current_user)) -> Lobby:
#     size = lobby.size
#     cards = [card(suit, value) for suit in range(4) for value in range(13)]
#     random.shuffle(cards)
#     game = Pesten(size, 8, cards)
#     # For debugging
#     # game = Pesten(2, 1, [
#     #     card(0, 0),
#     #     card(0, 0),
#     #     card(0, 0),
#     #     card(0, 0),
#     # ])
#     new_game = Lobby(game, user)
#     return new_game


class GameFactory:
    def create_game(self, size, user: str):
        cards = [card(suit, value) for suit in range(4) for value in range(13)]
        random.shuffle(cards)
        game = Pesten(size, 8, cards)
        # game = Pesten(2, 1, [
        #     card(0, 0),
        #     card(0, 0),
        #     card(0, 0),
        #     card(0, 0),
        # ])
        new_game = Lobby(game, user)
        return new_game


class HumanConnection:
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


lobbies: dict[str, Lobby] = {}
def get_lobbies():
    return lobbies

class Lobbies:
    # Fastapi dependency for lobby crud operations
    # TODO: Make ready for debug server.
    # TODO: Maybe put auth stuff also in here, so 'user' can be removed from endpoints
    def __init__(
            self,
            background_tasks: BackgroundTasks,
            user: str = Depends(get_current_user),
            game_factory: GameFactory = Depends(),
            lobbies: dict[str, Lobby] = Depends(get_lobbies)
    ):
        self.game_factory = game_factory
        self.background_tasks = background_tasks
        self.lobbies = lobbies
        self.user = user

    def get_lobbies(self):
        user = self.user
        return sorted([{
            'id': id,
            'size': len(lobby.players),
            'capacity': lobby.capacity,
            'creator': lobby.creator,
            'players': list(map(lambda p: p.name, lobby.players)),
        } for id, lobby in self.lobbies.items()], key=lambda lobby: lobby['creator'] != user)

    def get_lobby(self, lobby_name):
        return self.lobbies[lobby_name]

    def create_lobby(self, lobby_create: LobbyCreate):
        user = self.user
        if lobby_create.name in self.lobbies:
            raise HTTPException(status_code=400, detail="Lobby name already exists")
        new_game = self.game_factory.create_game(lobby_create.size, user)
        self.background_tasks.add_task(new_game.connect, Player(user, NullConnection()))

        logger.debug(f"Adding AI")
        async def connect_ais():
            asyncio.gather(*[
                new_game.connect(Player(f'AI{i+1}', AIConnection(new_game.game, i+1)))
                for i in range(lobby_create.aiCount)
            ])
        self.background_tasks.add_task(connect_ais)

        self.lobbies[lobby_create.name] = new_game
        return {
            'id': lobby_create.name,
            'size': 1 + lobby_create.aiCount,
            'capacity': new_game.capacity,
            'creator': user,
            'players': [user],
        }

    def delete_lobby(self, lobby_name):
        user = self.user
        try:
            lobby_to_be_deleted = self.lobbies[lobby_name]
        except KeyError as e:
            print(f'Lobby with name of {e} does not exist')
            raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
        if lobby_to_be_deleted.names[0] != user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you") # Contains FastAPI stuff
        print("deleting lobby")
        lobby = self.lobbies.pop(lobby_name)
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


class Connector:
    def __init__(self, lobbies = Depends(get_lobbies)):
        self.lobbies = lobbies

    async def connect_to_lobby(self, lobby_name: str, connection: HumanConnection):
        await connection.accept()
        try:
            lobby = self.lobbies[lobby_name]
        except KeyError as e:
            logger.error(f"Could not find {lobby_name} in lobbies")
            logger.error(f"Current lobbies: {self.lobbies}")
            return
        await lobby.connect(Player(connection.username, connection))
        # TODO: I don't like that the connector deletes the lobby
        if lobby.game.has_won and lobby_name in self.lobbies:
            logger.info(f"Deleting {lobby_name}")
            self.lobbies.pop(lobby_name)

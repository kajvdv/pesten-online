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
from pesten.rules import RULES_NAMES

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


def construct_rules(lobby: LobbyCreate):
    rules = {}
    if lobby.two:
        rules[0] = RULES_NAMES[lobby.two]

    if lobby.three:
        rules[1] = RULES_NAMES[lobby.three]

    if lobby.four:
        rules[2] = RULES_NAMES[lobby.four]

    if lobby.five:
        rules[3] = RULES_NAMES[lobby.five]

    if lobby.six:
        rules[4] = RULES_NAMES[lobby.six]

    if lobby.seven:
        rules[5] = RULES_NAMES[lobby.seven]

    if lobby.eight:
        rules[6] = RULES_NAMES[lobby.eight]

    if lobby.nine:
        rules[7] = RULES_NAMES[lobby.nine]

    if lobby.ten:
        rules[8] = RULES_NAMES[lobby.ten]

    if lobby.jack:
        rules[9] = RULES_NAMES[lobby.jack]

    if lobby.queen:
        rules[10] = RULES_NAMES[lobby.queen]

    if lobby.king:
        rules[11] = RULES_NAMES[lobby.king]

    if lobby.ace:
        rules[12] = RULES_NAMES[lobby.ace]

    return rules


class GameFactory:
    def create_game(self, size, rules, user: str):
        cards = [card(suit, value) for suit in range(4) for value in range(13)]
        random.shuffle(cards)
        game = Pesten(size, 8, cards, rules)
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
        rules = construct_rules(lobby_create)
        new_game = self.game_factory.create_game(lobby_create.size, rules, user)
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

    def delete_lobby(self, lobby_name, user):
        try:
            lobby_to_be_deleted = lobbies[lobby_name]
        except KeyError as e:
            logger.error(f'Lobby with name of {e} does not exist')
            raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
        if lobby_to_be_deleted.players[0].name != user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you") # Contains FastAPI stuff
        lobby = lobbies.pop(lobby_name)
        return {
            'id': lobby_name,
            'size': len(lobby.players),
            'capacity': lobby.capacity,
            'creator': user,
            'players': [p.name for p in lobby.players],
        }


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

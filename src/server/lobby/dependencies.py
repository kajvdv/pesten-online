from typing import Protocol
import asyncio
import logging
import json
import random

from fastapi import Depends, BackgroundTasks, status, Form
from fastapi.exceptions import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from server.auth import get_current_user
from pesten.pesten import Pesten, card
from pesten.rules import RULES_NAMES

from .schemas import LobbyCreate
from .lobby import Lobby, NullConnection, AIConnection, Player, ConnectionDisconnect


logger = logging.getLogger('uvicorn.error')


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


def construct_rules(lobby_create: LobbyCreate = Form()):
    rules = {}
    if lobby_create.two:
        rules[0] = lobby_create.two

    if lobby_create.three:
        rules[1] = lobby_create.three

    if lobby_create.four:
        rules[2] = lobby_create.four

    if lobby_create.five:
        rules[3] = lobby_create.five

    if lobby_create.six:
        rules[4] = lobby_create.six

    if lobby_create.seven:
        rules[5] = lobby_create.seven

    if lobby_create.eight:
        rules[6] = lobby_create.eight

    if lobby_create.nine:
        rules[7] = lobby_create.nine

    if lobby_create.ten:
        rules[8] = lobby_create.ten

    if lobby_create.jack:
        rules[9] = lobby_create.jack

    if lobby_create.queen:
        rules[10] = lobby_create.queen

    if lobby_create.king:
        rules[11] = lobby_create.king

    if lobby_create.ace:
        rules[12] = lobby_create.ace
    
    if lobby_create.joker:
        rules[77] = lobby_create.joker
        rules[78] = lobby_create.joker

    return rules


class GameFactory:
    def create_game(self, size, rules, jokerCount, user: str):
        cards = [card(suit, value) for suit in range(4) for value in range(13)]
        jokers = [77, 78]
        for i in range(jokerCount):
            cards.append(jokers[i%2])
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
            raise ConnectionDisconnect from e


lobbies: dict[str, Lobby] = {}
def get_lobbies():
    return lobbies

def get_lobby_name(lobby):
    for k, v in get_lobbies().items():
        if lobby == v:
            return k
    return None

def delete_lobby(lobby):
    for conn in [player.connection for player in lobby.players]: # Every gameloop of the lobby should stop when an AI stops
        asyncio.create_task(conn.close())

    for name, _lobby in get_lobbies().items():
        if lobby == _lobby:
            logger.info("Deleting lobbby")
            get_lobbies().pop(name)
            return
    logger.info("Could not find lobby to delete")

ai_tasks = set()
def connect_ais(lobby: Lobby, ai_count):
    # Important that this function is async, eventhough it is not using await
    # To make it work well when added to BackgroundTasks of Fastapi
    ai_connections = [AIConnection(lobby.game, i+1) for i in range(ai_count)]
    
    def done_callback(task: asyncio.Task):
        # Make sure everything closes if one AI stops
        execption = task.exception()
        if execption:
            logger.error(f"AI returned exception: {execption}")
        if get_lobby_name(lobby) not in get_lobbies():
            # Lobby is already deleted by another stopped AI
            return

        # Closing all connection and deleting lobby
        delete_lobby(lobby)

    name = get_lobby_name(lobby)
    for i in range(ai_count):
        # new_game.connect(Player(f'AI{i+1}', AIConnection(new_game.game, i+1)))
        task = asyncio.create_task(lobby.connect(Player(f'AI{i+1}', ai_connections[i])), name=f"{name}-AI-{i+1}")
        ai_tasks.add(task)
        task.add_done_callback(done_callback)
        task.add_done_callback(ai_tasks.discard)


def create_game(
        lobby_create: LobbyCreate = Form(),
        rules = Depends(construct_rules),
        user: str = Depends(get_current_user)
):
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    jokers = [77, 78]
    for i in range(lobby_create.jokerCount):
        cards.append(jokers[i%2])
    random.shuffle(cards)
    game = Pesten(lobby_create.size, 8, cards, rules)
    new_game = Lobby(game, user)
    return new_game


class Lobbies:
    def __init__(
            self,
            user: str = Depends(get_current_user),
            lobbies: dict[str, Lobby] = Depends(get_lobbies)
    ):
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
        } for id, lobby in self.lobbies.items() if not lobby.game.has_won], key=lambda lobby: lobby['creator'] != user)

    def get_lobby(self, lobby_name):
        return self.lobbies[lobby_name]

    async def create_lobby(self, lobby_name, ai_count, new_game: Pesten):
        user = self.user
        if lobby_name in self.lobbies:
            raise HTTPException(status_code=400, detail="Lobby name already exists")
        await new_game.connect(Player(user, NullConnection()))
        self.lobbies[lobby_name] = new_game
        connect_ais(new_game, ai_count)
        logger.info(f"New game created: {lobby_name}")
        return {
            'id': lobby_name,
            'size': 1 + ai_count,
            'capacity': new_game.capacity,
            'creator': user,
            'players': [user],
        }

    def delete_lobby(self, lobby_name):
        user = self.user
        try:
            lobby_to_be_deleted = lobbies[lobby_name]
        except KeyError as e:
            logger.error(f'Lobby with name of {e} does not exist')
            raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
        if lobby_to_be_deleted.players[0].name != user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you") # Contains FastAPI stuff
        for conn in [player.connection for player in lobby_to_be_deleted.players]:
            asyncio.create_task(conn.close())
        return {
            'id': lobby_name,
            'size': len(lobby_to_be_deleted.players),
            'capacity': lobby_to_be_deleted.capacity,
            'creator': user,
            'players': [p.name for p in lobby_to_be_deleted.players],
        }


class Connector:
    def __init__(self, lobbies = Depends(get_lobbies)):
        self.lobbies = lobbies

    async def connect_to_lobby(self, lobby_name: str, connection: HumanConnection):
        try:
            lobby = self.lobbies[lobby_name]
        except KeyError as e:
            logger.error(f"Could not find {lobby_name} in lobbies")
            logger.error(f"Current lobbies: {self.lobbies}")
            return
        player = Player(connection.username, connection)
        logger.info(f"Connecting {connection.username} to {lobby_name}")
        await lobby.connect(player)

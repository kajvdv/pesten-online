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
        except RuntimeError:
            pass

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


def create_game(
        lobby_create: LobbyCreate = Form(),
        rules = Depends(construct_rules),
):
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    jokers = [77, 78]
    for i in range(lobby_create.jokerCount):
        cards.append(jokers[i%2])
    random.shuffle(cards)
    game = Pesten(lobby_create.size, 8, cards, rules)
    return game

tasks = set()
class Lobbies:
    def __init__(
            self,
            user: str = Depends(get_current_user),
            lobbies: dict[str, Lobby] = Depends(get_lobbies)
    ):
        self.lobbies = lobbies
        self.user = user

    def get_lobbies(self):
        return self.lobbies

    def get_lobby(self, lobby_name):
        return self.lobbies[lobby_name]

    async def create_lobby(self, lobby_name, ai_count, game: Pesten):
        user = self.user
        if lobby_name in self.lobbies:
            raise HTTPException(status_code=400, detail="Lobby name already exists")        
        lobby = Lobby(game, user)
        #TODO: Have NullConnection for every initial player (for load_lobbies) 
        await lobby.connect(Player(user, NullConnection()))
        self.lobbies[lobby_name] = lobby
        for i in range(ai_count):
            connection = AIConnection(lobby.game, i+1)
            task = asyncio.create_task(lobby.connect(Player(f'AI{i+1}', connection)), name=f"{lobby_name}-AI-{i+1}")
            tasks.add(task) # Make sure task is not garbage collected
            task.add_done_callback(tasks.discard)
        logger.info(f"New game created: {lobby_name}")
        return lobby

    async def delete_lobby(self, lobby_name):
        user = self.user
        try:
            lobby_to_be_deleted = lobbies.pop(lobby_name)
        except KeyError as e:
            logger.error(f'Lobby with name of {e} does not exist')
            raise HTTPException(status.HTTP_404_NOT_FOUND, "This lobby does not exists")
        if lobby_to_be_deleted.players[0].name != user:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This lobby does not belong to you")

        for player in lobby_to_be_deleted.players:
            await player.connection.close()

        return lobby_to_be_deleted
        


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

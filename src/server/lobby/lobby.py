import asyncio
import logging
from typing import Protocol
import json

from pesten.pesten import Pesten
from pesten.agent import Agent

from .schemas import Board, Card


logger = logging.getLogger(__name__)


class ConnectionDisconnect(Exception):
    ...


class NullClosing(Exception):
    """This exception will prevent a NullConnection to get stuck in its gameloop inside Lobby.connect"""
    ...


class Connection(Protocol):
    async def accept(self): ...
    async def close(self): ...
    async def send_json(self, data): ...
    async def receive_text(self) -> str: ...


class NullConnection:
    async def accept(self): ...

    async def close(self): ...

    async def send_json(self, data): ...

    async def receive_text(self) -> str:
        raise NullClosing()
        

class AIConnection():
    def __init__(self, game: Pesten, player_index, delay = 1): # Resolve player_index automatically
        self.game = game
        self.agent = Agent(player_index)
        self.event = asyncio.Event()
        self.delay = delay

    async def accept(self):
        ...
    
    async def close(self):
        self.event.set() # Unblock if it was waiting on the event
    
    async def send_json(self, data: dict):
        # This function can trigger the event when it detects that its this AI its turn
        logger.debug(f"Received for {self.agent.player_index} : \n{json.dumps(data, indent=2)}")
        if 'error' in data:
            return
        if self.game.current_player == self.agent.player_index:
            logger.debug(f"{self.agent.player_index}: Setting the event")
            self.event.set()
            self.event.clear()
    
    async def receive_text(self) -> str:
        logger.debug(f"Waiting for event to be set on {self.agent.player_index}")
        await self.event.wait()
        logger.debug(f"{self.agent.player_index} generating choose")
        choose = self.agent.generate_choose(self.game)
        await asyncio.sleep(self.delay)
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
        # Maybe put try inside while?
        try:
            while not self.game.has_won:
                choose = await connection.receive_text()
                logger.debug(f"{new_player.name} choose {choose}")
                await self.play_choose(new_player, choose)
                logger.info(f"{new_player.name} successfully played a choose")
        except NullClosing as e:
            logger.debug("Null connection closing")
        except Exception as e:
            logger.error(f"Error in the connection: {e}")
        logger.info(f"{new_player.name} exited its gameloop")
                

    def update_boards(self, message=""):
        logger.debug("Updating player's board")
        asyncio.gather(*[
            player.connection.send_json(Board(
                topcard=Card.from_int(self.game.play_stack[-1]),
                previous_topcard=Card.from_int(self.game.play_stack[-2]) if len(self.game.play_stack) > 1 else None,
                can_draw=bool(self.game.draw_stack),
                choose_suit=self.game.asking_suit,
                draw_count=self.game.draw_count,
                current_player=self.players[self.game.current_player].name,
                otherPlayers={player.name: len(self.game.hands[self.players.index(player)]) for player in self.players},
                hand=[Card.from_int(card) for card in self.game.hands[player_id]],
                message=message
            ).model_dump())
            for player_id, player in enumerate(self.players)
        ])
            # asyncio.create_task(player.connection.send_json({**board.model_dump()}))

    
    def get_player_by_name(self, name: str) -> Player:
        try:
            player = next(filter(lambda p: p.name == name, self.players))
        except StopIteration as e:
            logger.info(f"Could not find {name} in the lobby")
            return None
        return player
        

    async def play_choose(self, player: Player, choose):
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
            await asyncio.gather(*[conn.close() for conn in connections])
        else:
            self.update_boards(message="")
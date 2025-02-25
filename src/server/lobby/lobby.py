import asyncio
import logging
from typing import Protocol
import json

from pesten.pesten import Pesten, CannotDraw, EndWithSpecialCard
from pesten.agent import Agent, AgentError

from .schemas import Board, Card


logger = logging.getLogger('uvicorn.error')


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
        self.messages = []
        self.exit = False

    async def accept(self):
        ...
    
    async def close(self):
        self.event.set() # makes it raise exception in receive_text method to stop loop
        self.exit = True
    
    async def send_json(self, data: dict):
        # This function can trigger the event when it detects that its this AI its turn
        # logger.debug(f"Received for {self.agent.player_index} : \n{json.dumps(data, indent=2)}")
        if 'error' in data:
            return
        if self.game.current_player == self.agent.player_index:
            # if len(self.messages) < 3:
            #     self.messages.append(data)
            # else:
            #     if all([msg["current_player"] == data["current_player"] for msg in self.messages]):
            #         raise Exception("AI is getting stuck")
            #     self.messages = []
            self.event.set()
    
    async def receive_text(self) -> str:
        await self.event.wait()
        self.event.clear()
        if self.exit:
            raise Exception("Closing AI")
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
        self.chooses = []


    async def connect(self, new_player: Player):
        name = new_player.name
        # Creates a gameloop for a connection
        if player := self.get_player_by_name(name):
            # Close the existing loop
            try:
                await player.connection.close()
            except Exception as e:
                logger.error(f"Error while closing a connection of an already joined player: {e}")
            # player = new_player This instead of the things below?
            index = self.players.index(player)
            self.players[index] = new_player # Replacing the player object
        elif self.started:
            raise Exception("Lobby is full")
        else:
            self.players.append(new_player)
        if len(self.players) == self.capacity:
            self.started = True
        await new_player.connection.accept() # Accept as late as possible
        connection = new_player.connection
        await self.update_boards(message=f"{name} joined the game")
        self.run = True
        # break-statements only make sure that the current connection stops
        while self.run:
            try:
                choose = await connection.receive_text()
                await self.play_choose(new_player, choose)
                self.run = not self.game.has_won # Stop all connections if game was won
            
            except AgentError as e:
                logger.error(f"Error in AI: {e}")
                self.run = False # Stop all connection when AI has error
            except CannotDraw as e:
                logger.error("Cannot draw")
                await new_player.connection.send_json({"error": "Cannot draw, you have to play a card"})
            except EndWithSpecialCard as e:
                logger.error("Player tried to end with special card")
                await new_player.connection.send_json({"error": "Cannot end with special card"})
            except NullClosing as e:
                logger.debug("Null connection closing")
                break
            except ConnectionDisconnect as e:
                logger.error(f"Player disconnected: {e}")
                break

    
    async def update_boards(self, message=""):
        for player_id, player in enumerate(self.players):
            send_coro = player.connection.send_json(Board(
                topcard=Card.from_int(self.game.play_stack[-1]),
                previous_topcard=Card.from_int(self.game.play_stack[-2]) if len(self.game.play_stack) > 1 else None,
                can_draw=bool(self.game.draw_stack),
                choose_suit=self.game.asking_suit,
                draw_count=self.game.draw_count,
                current_player=self.players[self.game.current_player].name,
                otherPlayers={
                    self.players[i].name
                    if i < len(self.players)else "": 
                    len(self.game.hands[i])
                    if i < len(self.players) else 0
                    for i in range(self.capacity)
                },
                hand=[Card.from_int(card) for card in self.game.hands[player_id]],
                message=message
            ).model_dump())
            logger.debug(f"Updating {self.players[self.game.current_player].name}'s board")
            await send_coro

    
    def get_player_by_name(self, name: str) -> Player:
        try:
            player = next(filter(lambda p: p.name == name, self.players))
        except StopIteration as e:
            return None
        return player
        

    async def play_choose(self, player: Player, choose):
        # player = self.get_player_by_name(name)
        name = player.name
        if not self.started:
            await player.connection.send_json({"error": "Game not started"})
            return
        if self.game.current_player != self.players.index(player):
            await player.connection.send_json({"error": "Not your turn"})
            return
        try:
            choose = int(choose)
        except ValueError:
            await player.connection.send_json({"error": "Invalid choose"})
            return
        log_count_before = len(self.game.logs)
        self.chooses.append(choose)
        self.game.play_turn(choose)
        if len(self.game.logs) != log_count_before:
            message = self.game.logs[-1][1]
        else:
            message = ""
        if self.game.has_won:
            await self.update_boards(f"{name} has won the game!")
            for conn in [player.connection for player in self.players]:
                await conn.close()
        else:
            await self.update_boards(message=message)
import logging
import asyncio
import json

from server.lobby import ConnectionDisconnect

logger = logging.getLogger(__name__)


class MockConnection:
    def __init__(self, username):
        self.username = username
        self.closed = False
        self.can_play = True
        self.receive_count = 1
    
    async def accept(self):
        logger.info("Accepted mock connection")

    async def close(self):
        if self.closed:
            raise ConnectionDisconnect("Connection already closed")
        logger.info(f"Closing mock connection of {self.username}")
        self.closed = True

    async def send_json(self, data):
        if self.closed:
            raise ConnectionDisconnect("Connection was closed")
        if "error" in data:
            self.can_play = False
        else:
            self.can_play = True
        logger.info(f"{self.username} received {json.dumps(data, indent=2)}")

    async def receive_text(self):
        if self.closed:
            raise ConnectionDisconnect("Connection was closed")
        if not self.can_play:
            await asyncio.sleep(1 * self.receive_count)
        self.receive_count += 1
        logger.info(f"{self.username} plays 1")
        return "1"

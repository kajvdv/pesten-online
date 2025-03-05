import shutil
from pathlib import Path
import asyncio
import random
import os

os.environ["ACCESS_TOKEN_SECRET"] = "123"
os.environ["REFRESH_TOKEN_SECRET"] = "123"

from pesten.pesten import Pesten, card
from server.lobby.lobby import Lobby
from server.lobby.dependencies import get_lobbies, Lobbies
from server.reload import save_lobbies, lobbies_dir

async def main(lobbies):
    lobbies_crud = Lobbies('admin', lobbies)
    
    # Creating games and adding them to the lobbies list
    game = Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {77: 'draw_card-5', 78: 'draw_card-5'})
    lobby = await lobbies_crud.create_lobby('jokers', 1, game)
    for p in lobby.players:
        await p.connection.close()

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Pesten(4, 8, cards, {
        9: 'change_suit',
        0: 'draw_card-2',
        5: 'another_turn',
        6: 'skip_turn',
        12: 'reverse_order',
    })
    lobby = await lobbies_crud.create_lobby("met regels", 3, game)
    for p in lobby.players:
        await p.connection.close()

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.shuffle(cards)
    game = Pesten(6, 8, cards, {
        0: 'draw_card-3',
        1: 'draw_card-3',
        2: 'draw_card-3',
        3: 'draw_card-3',
        4: 'draw_card-3',
        5: 'draw_card-3',
        6: 'draw_card-3',
        7: 'draw_card-3',
        8: 'draw_card-3',
        9: 'draw_card-3',
        10: 'draw_card-3',
        11: 'draw_card-3',
        12: 'draw_card-3',
    })
    lobby = await lobbies_crud.create_lobby("Alleen maar pakken", 5, game)
    for p in lobby.players:
        await p.connection.close()


if __name__ == "__main__":
    lobbies = {}
    asyncio.run(main(lobbies))
    save_lobbies(lobbies)






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
from server.lobby.routes import create_lobby_route
from server.lobby.schemas import LobbyCreate
from server.reload import save_lobbies, lobbies_dir

async def main(lobbies, lobbies_create_parameters):
    lobbies_crud = Lobbies('admin', lobbies)
    
    # Creating games and adding them to the lobbies list
    game = Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {77: 'draw_card-5', 78: 'draw_card-5'})
    # lobby = await lobbies_crud.create_lobby('jokers', 1, game)
    lobby_name = "jokers"
    lobby_create = LobbyCreate(
        name=lobby_name,
        size=2,
        aiCount=1,
        jokerCount=10,
        joker="draw_card-5"
    )
    await create_lobby_route(
        lobby_create,
        lobbies_crud,
        game,
        'admin',
        lobbies_create_parameters,
    )
    lobby = lobbies[lobby_name]
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
    # lobby = await lobbies_crud.create_lobby("met regels", 3, game)
    lobby_name = "met regels"
    lobby_create = LobbyCreate(
        name=lobby_name,
        size=4,
        aiCount=3,
        jokerCount=0,
        two='draw_card-2',
        seven='another_turn',
        eight='skip_turn',
        jack='change_suit',
        ace='reverse_order'
    )
    await create_lobby_route(
        lobby_create,
        lobbies_crud,
        game,
        'admin',
        lobbies_create_parameters,
    )
    lobby = lobbies[lobby_name]
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
    # lobby = await lobbies_crud.create_lobby("Alleen maar pakken", 5, game)
    lobby_name = "Alleen maar pakken"
    lobby_create = LobbyCreate(
        name=lobby_name,
        size=6,
        aiCount=5,
        jokerCount=0,
        two='draw_card-3',
        three='draw_card-3',
        four='draw_card-3',
        five='draw_card-3',
        six='draw_card-3',
        seven='draw_card-3',
        eight='draw_card-3',
        nine='draw_card-3',
        ten='draw_card-3',
        jack='draw_card-3',
        queen='draw_card-3',
        king='draw_card-3',
        ace='draw_card-3',
    )
    await create_lobby_route(
        lobby_create,
        lobbies_crud,
        game,
        'admin',
        lobbies_create_parameters,
    )
    lobby = lobbies[lobby_name]
    for p in lobby.players:
        await p.connection.close()


if __name__ == "__main__":
    lobbies = {}
    lobbies_create_parameters = {}
    asyncio.run(main(lobbies, lobbies_create_parameters))
    save_lobbies(lobbies, lobbies_create_parameters)






import json
import logging

from pesten.pesten import Pesten, card
from pesten.lobby import Game, get_lobby, create_lobby

logger = logging.getLogger(__name__)


def test_lobby_gets_deleted_after_winning_game(client):
    
    pesten = Pesten(2, 1, [
        # card(suit, value) for suit in range(4) for value in range(13)
        card(0, 0),
        card(0, 0),
        card(0, 0),
        card(0, 0),
    ])
    game = Game(pesten, '1')
    client.app.dependency_overrides[create_lobby] = lambda: game # Gets appended to the list of lobbies

    response = client.post("/lobbies", json={'size': 2}) # Addes the game defined in here
    response = client.get('/lobbies')
    assert len(response.json()) == 1
    game.game.has_won = True # 
    response = client.get('/lobbies')
    assert len(response.json()) == 0

    # client.app.dependency_overrides[get_lobby] = lambda: game

    # connection_1 = client.websocket_connect(f'lobbies/connect?name_override=1')
    # connection_2 = client.websocket_connect(f'lobbies/connect?name_override=2')
    # with connection_1, connection_2:
    #     board = connection_1.receive_json() # Receive update on first join
    #     board = connection_1.receive_json() # Receive update on second join
    #     board = connection_2.receive_json() # Receive update on second join
    #     logger.info("board: %s", json.dumps(board, indent=2))
    #     connection_1.send_text('1')
    #     board = connection_1.receive_json()
    #     logger.info("board: %s", json.dumps(board, indent=2))
    #     board = connection_1.receive_json()
    #     logger.info("board: %s", json.dumps(board, indent=2))
    # logger.info("End test")
    # assert game.game.has_won
import logging
from random import shuffle

from pesten.pesten import Pesten, card


logger = logging.getLogger(__name__)


def test_game():
    """Plays a game. Players just try playing cards until one of them wins"""
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    shuffle(cards)
    game = Pesten(4, 8, cards)
    curr = 0
    turn_count = 0
    while not game.has_won:
        choose = 1
        while True:
            new_curr = game.play_turn(choose)
            if choose == 0:
                break
            if new_curr != curr:
                curr = new_curr
                break
            choose += 1
            if choose >= len(game.curr_hand):
                choose = 0
        turn_count += 1
    logger.info(f"{turn_count=}")

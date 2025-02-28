import pickle
import logging
from random import shuffle, seed

from pesten.pesten import Pesten, card
from pesten.agent import Agent


logger = logging.getLogger(__name__)


def test_game():
    """Plays a game. Players just try playing cards until one of them wins"""
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    shuffle(cards)
    game = Pesten(4, 8, cards)
    curr = 0
    turn_count = 0
    while not game.has_won:
        choose = 0
        while True:
            new_curr = game.play_turn(choose)
            if choose < 0:
                break
            if new_curr != curr:
                curr = new_curr
                break
            choose += 1
            if choose >= len(game.curr_hand):
                choose = -1
        turn_count += 1
    logger.info(f"{turn_count=}")


def test_with_jokers():
    game = Pesten(2,2, [77,77,77,77,77,77,77,77,77,77,30,0,], {77: 'draw_card-5', 78: 'draw_card-5'})
    ai = Agent(99)

    current_player = 0
    chooses = [1, -1, 1, 1, 2, -1, 2, -1, 2, -1, 0, 1, -1, 0, 0]
    i = 0
    while i < len(chooses) or current_player == 1:
        logger.info(f"{i}: {current_player} - {game.current_hand()} {game.draw_count=}")
        if current_player == 0:
            assert game.check(chooses[i])
            current_player = game.play_turn(chooses[i])
            i += 1
        else:
            current_player = game.play_turn(ai.generate_choose(game))
    else:
        assert current_player == 0
        logger.info(f"{i}: {current_player} - {game.current_hand()} {game.draw_count=}")
    assert game.has_won


def test_reshuffle_on_empty_draw_stack():
    game = Pesten(2, 3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], {})
    while len(game.current_hand()) > 1:
        game.play_turn(0)
    while len(game.draw_stack) > 0:
        game.play_turn(-1)
    assert len(game.play_stack) > 1
    assert len(game.draw_stack) == 0
    assert game.play_stack == [12, 11, 10, 9, 8]
    game.play_turn(-1)
    assert game.play_stack == [8]
    assert game.draw_stack == [12, 9, 11]


def test_reshuffle_on_empty_draw_stack_odd():
    game = Pesten(2, 3, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], {})
    while len(game.current_hand()) > 1:
        game.play_turn(0)
    while len(game.draw_stack) > 0:
        game.play_turn(-1)
    assert len(game.play_stack) > 1
    assert len(game.draw_stack) == 0
    assert game.play_stack == [12, 11, 10, 9, 8]
    game.play_turn(0)
    game.play_turn(-1)
    assert game.play_stack == [7]
    assert game.draw_stack == [8, 9, 10, 11]

def test_shuffle():
    game = Pesten(2, 2, [1,2,3,4,5,6,7,8,9], {})
    game.shuffle()


def test_played_game():
    with open("tests/testgame.pickle", 'rb') as file:
        game, _, chooses, _ = pickle.load(file)

    reconstructed_game = Pesten(4, 8, game.init_cards, {
        9: 'change_suit',
        0: 'draw_card-2',
        5: 'another_turn',
        6: 'skip_turn',
        12: 'reverse_order',
    })
    for choose in chooses:
        assert not reconstructed_game.has_won
        reconstructed_game.play_turn(choose)
    assert reconstructed_game.has_won
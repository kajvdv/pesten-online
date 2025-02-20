import logging
import pytest

from pesten.pesten import Pesten
from pesten.game import print_game, deck

from pesten.rules import (
    drawCards,
    anotherTurn,
    skipTurn,
    reverseOrder,
    changeSuit,
)

logger = logging.getLogger(__name__)


@pytest.fixture()
def rules():
    return {
        0: drawCards,
        5: anotherTurn,
        6: skipTurn,
        9: changeSuit,
        11: anotherTurn,
        12: reverseOrder,
    }

def test_another_turn():
    game = Pesten(4, 2, [5,5,5,5,5,5,5,5,5,5,5], {5: 'another_turn'})
    assert game.play_turn(0) == 0
    assert game.current_player == 0

def test_skip_turn():
    game = Pesten(4, 2, [6,6,6,6,6,6,6,6,6,6,6], {6: 'skip_turn'})
    game.play_turn(0)
    assert game.current_player == 2

def test_reverse_order():
    game = Pesten(4, 2, [12,12,12,12,12,12,12,12,12,12,12], {12: 'reverse_order'})
    game.play_turn(0)
    assert game.current_player == 3

def test_draw_cards():
    game = Pesten(4, 2, [0,0,0,0,0,0,0,0,0,0,], {0: 'draw_card-2'})
    game.play_turn(0)
    game.play_turn(-1)
    assert len(game.hands[game.current_player]) == 4

def test_change_suit():
    game = Pesten(4, 2, [1,2,3,4+3*13,5,6,7,8,9,10,], {9: 'change_suit'})
#                                               ^ playstack
#                          ^3^2^1     ^0^3^2^1^0                                        
    assert game.play_turn(0) == 0
    assert game.play_turn(3) == 1
    assert game.play_turn(1) == 2
    assert game.play_turn(0) == 2


def test_change_suit_on_change_suit():
    game = Pesten(4, 2, [1,2,3,48,5,6,7,8,9,10,], {9: 'change_suit'})
#                                           ^ playstack
#                          ^3^2^1 ^0^3^2^1^0                                        
    assert game.play_turn(0) == 0
    assert game.play_turn(1) == 1
    assert game.play_turn(1) == 1
    assert game.play_turn(0) == 2
    assert game.play_turn(0) == 3


def test_dont_end_with_special_card():
    game = Pesten(2, 2, [0,0,0,0,0,0], {0: ""})
    assert game.play_turn(0) == 1
    assert game.play_turn(0) == 0
    assert game.play_turn(0) == 0
    assert game.logs[-1] == [0, "Can't end with rule card"]
    
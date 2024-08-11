from pesten import Pesten
from game import print_game, deck
import pytest

from rules import (
    drawCards,
    anotherTurn,
    skipTurn,
    reverseOrder,
    changeSuit,
)

def get_rules():
    return {
        0: drawCards,
        5: anotherTurn,
        6: skipTurn,
        9: changeSuit,
        11: anotherTurn,
        12: reverseOrder,
    }

@pytest.fixture()
def rules():
    return get_rules()

def test_another_turn(rules):
    game = Pesten(4, 2, [5,5,5,5,5,5,5,5,5,5,5], rules)
    game.play_turn(1)
    assert game.current_player == 0

def test_skip_turn(rules):
    game = Pesten(4, 2, [6,6,6,6,6,6,6,6,6,6,6], rules)
    game.play_turn(1)
    assert game.current_player == 2

def test_reverse_order(rules):
    game = Pesten(4, 2, [12,12,12,12,12,12,12,12,12,12,12], rules)
    game.play_turn(1)
    assert game.current_player == 3

def test_draw_cards(rules):
    game = Pesten(4, 2, [0,0,0,0,0,0,0,0,0,0,], rules)
    game.play_turn(1)
    assert len(game.hands[game.current_player]) == 4

def test_change_suit(rules):
    game = Pesten(4, 2, [1,2,3,4+3*13,5,6,7,8,9,10,], rules)
    game.play_turn(1)
    game.play_turn(4)
    game.play_turn(1)
    game.play_turn(2)
    assert game.current_player == 2



if __name__ == "__main__":
    test_change_suit(get_rules())

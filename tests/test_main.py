import pytest

from main import *


def test_warning_if_cannot_draw():
    card_count = 10
    def test_turn(player):
        return -1
            
    with pytest.raises(CannotDraw):
        play_game(
            ['test_player'],
            [Card('test', 'test') for _ in range(card_count)],
            test_turn,
        )
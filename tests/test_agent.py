import logging
import random

import pytest


logger = logging.getLogger(__name__)


def test_agent_super_simple():
    from pesten.pesten import Pesten, card
    from pesten.agent import Agent
    game = Pesten(2, 1, [
        card(0, 0),
        card(0, 0),
        card(0, 0),
        card(0, 0),
    ])
    agent = Agent() 
    choose = agent.generate_choose(game)
    game.play_turn(choose)
    assert game.has_won


def test_agent_infinite_loop_detection():
    from pesten.pesten import Pesten, card
    from pesten.agent import Agent
    game = Pesten(2, 1, [
        card(0, 4),
        card(1, 5),
        card(2, 6),
        card(3, 7),
    ])
    agent = Agent()
    with pytest.raises(Exception):
        while not game.has_won: 
            choose = agent.generate_choose(game)
            game.play_turn(choose)


def test_agent_full_game():
    from pesten.pesten import Pesten, card
    from pesten.agent import Agent
    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.seed(1)
    random.shuffle(cards)
    game = Pesten(2, 1, cards)
    agent = Agent() # One agent for multiple players
    while not game.has_won:
        choose = agent.generate_choose(game)
        game.play_turn(choose)

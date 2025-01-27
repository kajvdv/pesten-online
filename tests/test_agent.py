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
    agent = Agent(0) 
    agent.play_turn(game)
    assert game.has_won


def test_agent_agent_error():
    from pesten.pesten import Pesten, card
    from pesten.agent import Agent, AgentError

    game = Pesten(2, 1, [
        card(0, 4),
        card(1, 5),
        card(2, 6),
        card(3, 7),
    ])
    agents = [Agent(i) for i in range(2)]
    with pytest.raises(AgentError):
        while not game.has_won: 
            agents[game.current_player].play_turn(game)


def test_agent_full_game():
    from pesten.pesten import Pesten, card
    from pesten.agent import Agent

    cards = [card(suit, value) for suit in range(4) for value in range(13)]
    random.seed(1)
    random.shuffle(cards)
    game = Pesten(2, 1, cards)
    agents = [Agent(i) for i in range(2)]
    turn_counter = 0
    while not game.has_won:
        choose = agents[turn_counter % 2].generate_choose(game)
        game.play_turn(choose)
        turn_counter += 1
    logger.info(f"Total amount of turns {turn_counter}")

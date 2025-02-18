import logging

from pesten.pesten import Pesten


logger = logging.getLogger(__name__)


class AgentError(Exception):
    ...


class Agent:
    def __init__(self, player_index):
        self.player_index = player_index

    
    def get_possible_chooses(self, game: Pesten):
        card_count = len(game.curr_hand)
        possible_choosese = []
        for possible_choose in range(card_count):
            if game.check(possible_choose):
                possible_choosese.append(possible_choose)
        return possible_choosese
    

    def generate_choose(self, game: Pesten):
        possible_choosese = self.get_possible_chooses(game)
        if possible_choosese:
            choose = possible_choosese[0]
        else:
            game.assert_can_draw()
            choose = -1
        
        if game.asking_suit:
            choose = 0
        elif game.draw_count > 0:
            choose = -1
        return choose

    
    def play_turn(self, game: Pesten):
        assert game.current_player == self.player_index
        if game.asking_suit:
            choose = 0
        elif game.drawing:
            choose = -1
        choose = self.generate_choose(game)
        try:
            topcard = game.play_stack[-1]
            index_next_player = game.play_turn(choose)
            if not game.has_won and index_next_player == self.player_index and topcard == game.play_stack[-1]:
                # If the turn stays the same and the topcard the same then the choose was not good
                raise AgentError("Wrong choose generated")
        except AgentError as e:
            raise e
        except Exception as e:
            raise AgentError("AI got an error", e)

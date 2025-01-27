import logging

from pesten.pesten import Pesten


logger = logging.getLogger(__name__)



class Agent:
    def __init__(self):
        self.last_choose = 9999 # Choose it would never generate
        self.last_player = 9999 # Same
        self.last_top_card = None

    
    def get_possible_chooses(self, game: Pesten):
        card_count = len(game.curr_hand)
        possible_choosese = []
        for possible_choose in range(1, card_count + 1):
            if game.check(possible_choose - 1): # From player perspective to game perspective
                possible_choosese.append(possible_choose)
        return possible_choosese
    

    def generate_choose(self, game: Pesten):
        possible_choosese = self.get_possible_chooses(game)
        if possible_choosese:
            choose = possible_choosese[0]
        else:
            choose = 0
        
        if self.last_top_card == game.play_stack[-1]:
            if game.curr_hand == self.last_hand and choose == self.last_choose:
                logger.error("Agent generated the same choose for the same hand. Detected going in infinite loop")
                raise Exception("Agent going in infinite loop")
        self.last_choose = choose
        self.last_hand = list(game.curr_hand)
        self.last_top_card = game.play_stack[-1]
        return choose
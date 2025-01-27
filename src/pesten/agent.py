import logging

from pesten.pesten import Pesten


logger = logging.getLogger(__name__)



class Agent:
    # This agent generates the choses for all the player in a game.
    # TODO: Make agent only concern one player.
    def __init__(self):
        self.last_choose = 9999 # Choose it would never generate
        self.last_player = 9999 # Same

    
    def get_possible_chooses(self, game: Pesten):
        card_count = len(game.curr_hand)
        possible_choosese = []
        for possible_choose in range(1, card_count + 1):
            if game.check(possible_choose - 1): # From player perspective to game perspective
                possible_choosese.append(possible_choose)
        return possible_choosese
    

    def update(self, game: Pesten):
        # Updates the the board for the agent
        self.last_player = game.current_player
        self.last_hand = list(game.curr_hand)


    def generate_choose(self, game: Pesten):
        self.update(game) # Make sure the agent has the current state of the game
        possible_choosese = self.get_possible_chooses(game)
        if possible_choosese:
            choose = possible_choosese[0]
        else:
            choose = 0
        if self.last_player == game.current_player:
            logger.info("Current player was also the last player")
            if game.curr_hand == self.last_hand and choose == self.last_choose:
                logger.error("Agent generated the same choose for the same hand. Detected going in infinite loop")
                raise Exception("Agent going in infinite loop")
        self.last_choose = choose
        return choose
import logging
from random import shuffle
from time import sleep
from typing import Literal
from pesten.rules import drawCards, anotherTurn, skipTurn, reverseOrder

logger = logging.getLogger(__name__)

# SUITS = ["Harten", "Ruiten", "Schoppen", "Klaver"]
# VALUES = ["Twee", "Drie", "Vier", "Vijf", "Zes", "Zeven", "Acht", "Negen", "Tien", "Boer", "Vrouw", "Heer", "Aas"]

SUITS = ["hearts", "diamonds", "spades", "clubs"]
VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
BLACK_JOKER = 77
RED_JOKER = 78

def card(suit, value):
    # suit: 0-4, value 0-13
    return suit*13 + value


def card_string(c):
    if c >= 52:
        value = 'mirror'
    else:
        value = VALUES[c % 13]
    return SUITS[(c // 13) % 4] + " " + value


class CannotDraw(Exception):
    pass


class Pesten:
    def __init__(self, player_count: int, hand_count, cards: list, rules: dict = {}) -> None:
        self.player_count = player_count
        self.current_player = 0
        self.draw_stack = cards
        self.play_stack = [cards.pop()]
        self.hands = [[] for _ in range(player_count)]
        self.curr_hand = self.hands[self.current_player]
        self.reverse = False
        self.rules = rules
        self.change_suit_state: Literal["not asked", "asking", "asked"] = "not_asked"
        self.drawing = False
        self.draw_count = 0
        for _ in range(hand_count):
            for hand in self.hands:
                hand.append(self.draw_stack.pop())
        self.has_won = False
        self.asking_suit = False
        self.enable_logging = False
        self.logs = []


    def shuffle(self):
        new_stack = []
        while len(self.draw_stack) > 1:
            new_stack.append(self.draw_stack.pop(-1))
            new_stack.append(self.draw_stack.pop(0))
        if len(self.draw_stack) == 1:
            new_stack.append(self.draw_stack.pop())
        assert not self.draw_stack
        self.draw_stack = new_stack
    
    
    def assert_can_draw(self):
        if len(self.draw_stack) + len(self.play_stack) <= 1:
            raise CannotDraw("Not enough cards on the board to draw. Please play a card")

    
    def log(self, message):
        if not self.enable_logging:
            return
        data = [self.current_player, message]
        if len(self.logs) > 0 and data == self.logs[-1]:
            return
        self.logs.append(data)


    def draw(self):
        self.assert_can_draw()
        if not self.draw_stack and len(self.play_stack) > 1:
            top_card = self.play_stack.pop()
            while self.play_stack:
                card = self.play_stack.pop()
                if card >= 52 and card != BLACK_JOKER and card != RED_JOKER:
                    # These were added when choosing suit. Don't put back in draw stack
                    continue
                self.draw_stack.append(card)
            for _ in range(100):
                self.shuffle()
            self.play_stack.append(top_card)
        self.curr_hand.append(self.draw_stack.pop())


    def check(self, choose):
        played_card = self.curr_hand[choose]
        top_card = self.play_stack[-1]
        if played_card == BLACK_JOKER or played_card == RED_JOKER or top_card == BLACK_JOKER or top_card == RED_JOKER:
            return True
        suit_top_card = (top_card // 13) % 4 # There should only be 52 cards with 51 being the highest
        can_play = played_card // 13 == suit_top_card or played_card % 13 == top_card % 13
        if can_play:
            self.log(f"Choose {choose}")
        # Not allowed to end with special card
        #TODO: Make this configurable
        #TODO: Joker can by-pass this
        is_special = (played_card % 13) in self.rules
        if is_special and len(self.current_hand()) == 1:
            self.log("Can't end with rule card")
            return False
        return can_play


    def play(self, choose):
        self.play_stack.append(self.curr_hand.pop(choose))
        if not self.curr_hand:
            self.log("The game was won!")
            self.has_won = True


    def next(self):
        if self.has_won:
            return
        if not self.reverse:
            self.current_player += 1
        else:
            self.current_player -= 1
        self.current_player += self.player_count # Make sure it is a positive number
        self.current_player %= self.player_count # before modding
        self.curr_hand = self.hands[self.current_player]


    def resolve_rule(self, choose):
        value_choose = self.curr_hand[choose]
        if value_choose != BLACK_JOKER and value_choose != RED_JOKER:
            value_choose = value_choose % 13
        return self.rules.get(value_choose, "")
        

    def _play_turn(self, choose) -> int:
        # Returns index player who's next turn will come from.
        # If choose is negative it will draw a card

        # I explicitly return in all cases to be explicit about the flow
        if self.has_won:
            return int(self.current_player)


        if self.asking_suit:
            if choose >= len(SUITS):
                # Asking again
                return self.current_player
            self.chosen_suit = choose
            value_card = self.play_stack[-1] % 13
            suit_card = 52 + choose * 13 + value_card
            self.log(f"Suit choosen: {SUITS[choose]}")
            self.play_stack.append(suit_card) # Will be removed on reshuffling deck
            self.next()
            self.asking_suit = False
            return self.current_player


        if self.draw_count > 0:
            if choose < 0:
                self.log(f"Has to draw {self.draw_count}")
                for _ in range(self.draw_count):
                    try:
                        self.draw()
                    except CannotDraw:
                        self.log(f"Not enough cards to draw {self.draw_count}")
                        break
                self.draw_count = 0
                return self.current_player
            rule = self.resolve_rule(choose)
            if 'draw_card' not in rule or not self.check(choose):
                return self.current_player
            self.log("Countered with another draw card")
            # Continue as normal because I'm sure it will enter the draw_card if-block later

        if choose < 0:
            self.log("Drawing card")
            self.draw()
            self.next()
            return int(self.current_player)

        if choose < len(self.curr_hand):
            rule = self.resolve_rule(choose)
            if rule == 'another_turn':
                if self.check(choose):
                    self.log(f"Another turn {card_string(self.curr_hand[choose])}")
                    self.play(choose)
                return self.current_player
            
            if rule == 'skip_turn':
                if self.check(choose):
                    self.log(f'skip turn with {card_string(self.curr_hand[choose])}')
                    self.play(choose)
                    self.next()
                    self.next()
                return self.current_player
            
            if rule == 'reverse_order':
                if self.check(choose):
                    self.log(f'reverse order with {card_string(self.curr_hand[choose])}')
                    self.play(choose)
                    self.reverse = not self.reverse
                    self.next()
                return self.current_player

            if rule and 'draw_card' in rule:
                if self.check(choose):
                    _, count = rule.split("-")
                    self.draw_count += int(count)
                    self.log(f'draw card with {card_string(self.curr_hand[choose])}. counter: {self.draw_count}')
                    self.play(choose)
                    # self.drawing = True
                    self.next()
                return self.current_player

            if rule == 'change_suit':
                if self.check(choose):
                    self.log(f'changed suit with {card_string(self.curr_hand[choose])}')
                    self.play(choose)
                    self.asking_suit = True
                return self.current_player
                
            # default play
            if self.check(choose):
                self.log(f"played {card_string(self.curr_hand[choose])}")
                self.play(choose)       
                self.next()
            return self.current_player
        # logger.info("Invalid choose")
        return self.current_player
    
    def play_turn(self, choose) -> int:
        self.enable_logging = True # Makes sure logs are only added by this function
        current_player = self._play_turn(choose)
        self.enable_logging = False
        return current_player

    def current_hand(self):
        return self.hands[self.current_player]

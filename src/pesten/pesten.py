from random import shuffle
from time import sleep
from typing import Literal
from pesten.rules import drawCards, anotherTurn, skipTurn, reverseOrder

# SUITS = ["Harten", "Ruiten", "Schoppen", "Klaver"]
# VALUES = ["Twee", "Drie", "Vier", "Vijf", "Zes", "Zeven", "Acht", "Negen", "Tien", "Boer", "Vrouw", "Heer", "Aas"]

SUITS = ["hearts", "diamonds", "spades", "clubs"]
VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]


def card(suit, value):
    # suit: 0-4, value 0-13
    return suit*13 + value


def card_string(c):
    return SUITS[c // 13] + " " + VALUES[c % 13]


class CannotDraw(Exception):
    pass


class Pesten:
    #TODO move all changeSuit logic to rule function 
    def __init__(self, player_count: int, hand_count, cards: list, rules: dict = {}) -> None:
        # I dont't like current players and curr_hand being in diffirent places
        self.player_count = player_count
        self.current_player = 0
        self.draw_stack = cards
        self.play_stack = [cards.pop()]
        self.hands = [[] for _ in range(player_count)]
        self.curr_hand = self.hands[self.current_player]
        self.reverse = False
        self.rules = rules
        self.change_suit_state: Literal["not asked", "asking", "asked"] = "not_asked"
        for _ in range(hand_count):
            for hand in self.hands:
                hand.append(self.draw_stack.pop())
        self.has_won = False
        self.asking_suit = False

    def draw(self):
        if len(self.draw_stack) + len(self.play_stack) <= 1:
            raise CannotDraw("Not enough cards on the board to draw. Please play a card")
        if not self.draw_stack and len(self.play_stack) > 1:
            top_card = self.play_stack.pop()
            shuffle(self.play_stack)
            while self.play_stack:
                self.draw_stack.append(self.play_stack.pop())
            self.play_stack.append(top_card)
        self.curr_hand.append(self.draw_stack.pop())

    def check(self, choose):
        played_card = self.curr_hand[choose]
        top_card = self.play_stack[-1]
        suit_top_card = top_card // 13
        if self.change_suit_state == "asked":
            suit_top_card = self.chosen_suit
        return played_card // 13 == suit_top_card or played_card % 13 == top_card % 13

    def play(self, choose):
        self.play_stack.append(self.curr_hand.pop(choose))

    def next(self):
        if not self.reverse:
            self.current_player += 1
        else:
            self.current_player -= 1
        self.current_player += self.player_count # Make sure it is a positive number
        self.current_player %= self.player_count
        self.curr_hand = self.hands[self.current_player]
        
    def play_turn(self, choose) -> int:
        # Returns index next player
        if self.has_won:
            return int(self.current_player)
        if choose == 0 and self.asking_suit == False:
            self.draw()
            self.next()
        else:
            choose = choose - 1 # player perspective to game perspective
            if self.change_suit_state == "asking" and choose < len(SUITS):
                print("Suit chosen", SUITS[choose])
                self.chosen_suit = choose
                self.change_suit_state = "asked"
                self.next()
            elif choose < len(self.curr_hand):
                value_choose = self.curr_hand[choose] % 13
                rule = self.rules.get(value_choose, None)
                if rule:
                    rule(self, choose)
                else:
                    # default play 
                    if self.check(choose): # Question: Should check receive the corrected choose?
                        self.change_suit_state = "not asked"
                        self.play(choose)
                        if self.curr_hand:
                            self.next()
                        else:
                            self.has_won = True        
        return int(self.current_player)
    
    def current_hand(self):
        return self.hands[self.current_hand]

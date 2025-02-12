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
        self.drawing = False
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
                card = self.play_stack.pop()
                if card >= 52:
                    # These were added when choosing suit. Don't put back
                    continue
                self.draw_stack.append(card)
            self.play_stack.append(top_card)
        self.curr_hand.append(self.draw_stack.pop())


    def check(self, choose):
        # TODO: Check if the choose is a special card and a last one
        played_card = self.curr_hand[choose]
        top_card = self.play_stack[-1]
        suit_top_card = (top_card // 13) % 4 # There should only be 52 cards with 51 being the highest
        return played_card // 13 == suit_top_card or played_card % 13 == top_card % 13


    def play(self, choose):
        self.play_stack.append(self.curr_hand.pop(choose))
        if not self.curr_hand:
            self.has_won = True 


    def next(self):
        if self.has_won:
            return
        if not self.reverse:
            self.current_player += 1
        else:
            self.current_player -= 1
        self.current_player += self.player_count # Make sure it is a positive number
        self.current_player %= self.player_count
        self.curr_hand = self.hands[self.current_player]
        

    def play_turn(self, choose) -> int:
        # Returns index player who's next turn will come from.
        # If choose is negative it will draw a card

        # I explicitly return in all cases to be explicit about the flow
        if self.has_won:
            return int(self.current_player)
        
        if self.drawing:
            if choose < 0:
                self.draw()
                self.draw()
            return self.current_player

        if self.asking_suit:
            if choose >= len(SUITS):
                # Asking again
                return self.current_player
            self.chosen_suit = choose
            value_card = self.play_stack[-1] % 13
            suit_card = 52 + choose * 13 + value_card
            self.play_stack.append(suit_card) # Will be removed on reshuffling deck
            self.next()
            self.asking_suit = False
            return self.current_player


        if choose < 0:
            self.draw()
            self.next()
            return int(self.current_player)

        
        if choose < len(self.curr_hand):
            value_choose = self.curr_hand[choose] % 13
            rule = self.rules.get(value_choose, None)
            if rule == 'another_turn':
                if self.check(choose):
                    self.play(choose)
                return self.current_player
            
            if rule == 'skip_turn':
                if self.check(choose):
                    self.play(choose)
                    self.next()
                    self.next()
                return self.current_player
            
            if rule == 'reverse_order':
                if self.check(choose):
                    self.play(choose)
                    self.reverse = not self.reverse
                    self.next()
                return self.current_player

            if rule == 'draw_card':
                if self.check(choose):
                    self.play(choose)
                    self.drawing = True
                    self.next()
                return self.current_player

            if rule == 'change_suit':
                if self.check(choose):
                    self.play(choose)
                    self.asking_suit = True
                return self.current_player
                
            # default play
            if self.check(choose):
                self.play(choose)       
                self.next()
            return self.current_player
        return self.current_player
    

    def current_hand(self):
        return self.hands[self.current_hand]

from random import shuffle
from time import sleep

SUITS = ["Harten", "Ruiten", "Schoppen", "Klaver"]
VALUES = ["Twee", "Drie", "Vier", "Vijf", "Zes", "Zeven", "Acht", "Negen", "Tien", "Boer", "Vrouw", "Heer", "Aas"]


def card(suit, value):
    # suit: 0-4, value 0-13
    return suit*13 + value


def card_string(c):
    return SUITS[c // 13] + " " + VALUES[c % 13]


class CannotDraw(Exception):
    pass


class Pesten:
    def __init__(self, player_count: int, hand_count, cards: list) -> None:
        self.player_count = player_count
        self.current_player = 0
        self.draw_stack = cards
        self.play_stack = [cards.pop()]
        self.hands = [[] for _ in range(player_count)]
        self.curr_hand = self.hands[self.current_player]
        for _ in range(hand_count):
            for hand in self.hands:
                hand.append(self.draw_stack.pop())
        self.has_won = False

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

    def play(self, choose):
        played_card = self.curr_hand[choose]
        top_card = self.play_stack[-1]
        if played_card // 13 == top_card // 13 or played_card % 13 == top_card % 13:
            self.play_stack.append(self.curr_hand.pop(choose))
            return True
        return False

    def next(self):
        self.current_player += self.player_count + 1 # Make sure it is a positive number
        self.current_player %= self.player_count
        self.curr_hand = self.hands[self.current_player]
    
    def play_turn(self, choose) -> int:
        # Returns index next player
        if self.has_won:
            return int(self.current_player)
        
        if choose == 0:
            self.draw()
            self.next()
        else:
            choose = choose - 1 # player perspective to game perspective
            if choose < len(self.curr_hand):
                if self.play(choose):
                    if self.curr_hand:
                        self.next()
                    else:
                        self.has_won = True        
        return int(self.current_player)
        


if __name__ == "__main__":
    while True:
        cards = [card(suit, value) for suit in range(4) for value in range(13)]
        shuffle(cards)
        game = Pesten(4, 8, cards)
        curr = 0
        while not game.has_won:
            print(game.current_player, 'aan zet')
            print("topcard is", card_string(game.play_stack[-1]))
            for i, c in enumerate(game.curr_hand, start=1):
                print(i, card_string(c))
            print("Wat is je keuze: ")
            choose = 1
            while True:
                new_curr = game.play_turn(choose)
                if choose == 0:
                    break
                if new_curr != curr:
                    print(choose, "was goed")
                    curr = new_curr
                    break
                print(choose, 'was niet goed')
                choose += 1
                if choose >= len(game.curr_hand):
                    print("kaart trekken")
                    choose = 0

        else:
            print(game.current_player, "has won!")
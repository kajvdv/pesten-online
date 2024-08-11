"""A small client to play and test the game"""
from random import shuffle
from pesten import card, card_string, Pesten


def print_game(game):
    print(game.current_player, 'aan zet')
    print("topcard is", card_string(game.play_stack[-1]))
    for i, c in enumerate(game.curr_hand, start=1):
        print(i, card_string(c))


def deck():
    return [card(suit, value) for suit in range(4) for value in range(13)]


if __name__ == "__main__":
    while True:
        cards = deck()
        shuffle(cards)
        game = Pesten(4, 8, cards)
        curr = 0
        while not game.has_won:
            print_game(game)
            choose = input("Wat is je keuze: ")
            choose = int(choose)
            new_curr = game.play_turn(choose)
            if new_curr != curr:
                print(choose, "was goed")
            else:
                print(choose, 'was niet goed')
            curr = new_curr

        else:
            print(game.current_player, "has won!")
import sys
from dataclasses import dataclass, field
import json
from random import shuffle


class CannotDraw(Exception):
    pass


@dataclass
class Card:
    suit: str
    value: str

    def __repr__(self) -> str:
        return self.suit + " " + self.value


@dataclass
class Player:
    name: str
    hand: list[Card] = field(default_factory=list)

    def __repr__(self) -> str:
        return self.name


def print_deck(deck: list[Card], print_index: bool = False):
    string = ""
    for i, card in enumerate(deck, start=1):
        if print_index:
            string += str(i)+": " + str(card) + '\n'
    return string

def move_card(source: list[Card], destination: list[Card], index = -1):
    destination.append(source.pop(index))

def get_next_player_index(current_index, players):
    return (current_index + 1) % len(players)

def get_choose():
    return int(input("Welke kaart kies je? ")) - 1

suits = ["Harten", "Ruiten", "Schoppen", "Klaver"]
values = ["Twee", "Drie", "Vier", "Vijf", "Zes", "Zeven", "Acht", "Negen", "Tien", "Boer", "Vrouw", "Heer", "Aas"]

class Pesten:
    def __init__(self, draw_deck, play_deck, players: list[Player]):
        self.draw_deck = draw_deck
        self.play_deck = play_deck
        self.players = players
        self.curr_player_index = 0
        
    def init_game(self):
        self.draw_deck = []

    def play_turn(self):
        while(True):
            index = input("Choose card")
            if not value.isdigit():
                print("Choose must be a digit")
                continue
            value = int(index) - 1
            if value < 0:
                print("Player choose to draw a card")
                if len(self.draw_deck) + len(self.play_deck) <= 1:
                    print("There are not enough cards on the board to draw one. Please play a card. If you can't then you have broken the game, stupid...")
            else:
                print("Player choose card")
            return value

    def get_current_player(self):
        return self.players[self.curr_player_index]

    def play_card(self, index):
        card = self.get_current_player().hand.pop(index)
        self.play_deck.append(card)

    def reshuffle_board(self):
        top_card = self.play_deck.pop()
        while(self.play_deck):
            self.draw_deck.append(self.play_deck.pop())
        for _ in range(13):
            start = 0 
            end = len(self.draw_deck) - 1
            while(start < end):
                shuffle_deck = []
                shuffle_deck.append(self.draw_deck[end])
                shuffle_deck.append(self.draw_deck[start])
                start += 1
                end -= 1
                self.draw_deck = shuffle_deck
        self.play_deck.append(top_card)

    def draw_card(self):
        if len(self.draw_deck) <= 0:
            self.reshuffle_board()
        card = self.draw_deck.pop()
        self.get_current_player().hand.append(card)
    
    def decide_next_player(self):
        pass
        



def create_new_game(players: list[str]):
    players = [Player(name) for name in players]
    deck_draw = [Card(suit, value) for suit in suits for value in values]
    shuffle(deck_draw)
    game = Pesten()

invalid_card_played_message = "Ongeldige kaart gespeeld, speel nog een keer"
    
def play_game(player_names: list[str]):
    deck_draw = [Card(suit, value) for suit in suits for value in values]
    shuffle(deck_draw)
    # Create the players
    players = [Player(name) for name in player_names]
    # Devide the cards over the players
    for player in players:
        for _ in range(8):
            move_card(deck_draw, player.hand)
    # Put a card on the play deck
    deck_play = []
    move_card(deck_draw, deck_play)
    # Print the board with the current players hand
    index_current_player = 0
    while(True):
        current_player = players[index_current_player]
        print(dir(players[0]), file=sys.stderr)
        choose = int(input(json.dumps({
            "drawDeck": [str(card) for card in deck_draw],
            "playDeck": [str(card) for card in deck_play],
            "players": [{'name': player.name, "hand": [str(card) for card in player.hand]} for player in players],
            "topCard": str(deck_play[-1]),
            "currentPlayer": current_player.name,
            "hand": list(map(str, current_player.hand)),
        }) + '\n')) - 1
        # Draw card when player pressed 0
        if choose == -1:
            if deck_draw:
                move_card(deck_draw, current_player.hand)
                index_current_player = get_next_player_index(index_current_player, players)
            elif len(deck_play) > 1:
                # Reshuffle cards from play deck
                topcard = deck_play.pop()
                shuffle(deck_play)
                while(deck_play):
                    move_card(deck_play, deck_draw)
                deck_play.append(topcard)
            else:
                print("No enough cards on the board", file=sys.stderr)
        else:
            chosen_card = current_player.hand[choose]

            # Check if either suit or value is the same
            topcard = deck_play[-1]
            if topcard.suit == chosen_card.suit or topcard.value == chosen_card.value:
                # Valid play. Move card and go to the next player
                move_card(current_player.hand, deck_play, choose)
                # Check if won
                if not current_player.hand:
                    print(current_player.name, "has won!")
                    break
                index_current_player = get_next_player_index(index_current_player, players)
            else:
                print("Choose was not valid", file=sys.stderr)
        print(index_current_player)

if __name__ == "__main__":
    print("start new game", file=sys.stderr)
    player_names = ["Kaj", "Soy"]
    play_game(player_names)
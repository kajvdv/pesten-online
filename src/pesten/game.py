from typing_extensions import Protocol


SUITS = ["Harten", "Ruiten", "Schoppen", "Klaver"]
VALUES = ["Twee", "Drie", "Vier", "Vijf", "Zes", "Zeven", "Acht", "Negen", "Tien", "Boer", "Vrouw", "Heer", "Aas"]


class Card:
    def __init__(self, suit, value) -> None:
        self.suit = suit
        self.value = value

    def is_same_suit(self, other_card):
        if self is other_card:
            return False
        return self.suit == other_card.suit or other_card.is_same_suit(other_card)

    def is_same_value(self, other_card):
        if self is other_card:
            return False
        return self.value == other_card.value or other_card.is_same_suit(other_card)

    def __repr__(self) -> str:
        return self.suit + " " + self.value


class Deck:
    def __init__(self, cards) -> None:
        # self.cards = [Card(suit, value) for suit in suits for value in values]
        self.cards = cards

    def shuffle(self):
        new_cards = []
        start = 0
        end = len(self.cards) - 1
        while(start < end):
            new_cards.append(self.cards[end])
            new_cards.append(self.cards[start])
            start += 1
            end -= 1
        self.cards = new_cards

    def take(self, index=-1):
        return self.cards.pop(index)
    
    def add(self, card):
        self.cards.append(card)
    
    def is_empty(self):
        return len(self.cards) == 0

    def __repr__(self) -> str:
        return str(self.cards)
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]


def create_full_deck():
    return Deck([Card(suit, value) for suit in SUITS for value in VALUES])
    

class Player:
    def __init__(self, name) -> None:
        self.name = name
        self.hand: list[Card] = []
    
    def give_card(self, card):
        self.hand.append(card)

    def take_card(self, index):
        card = self.hand.pop(index)
        return card
    

class PlayerGroup:
    def __init__(self, players) -> None:
        self.players: list[Player] = players
        self.index_current_player = 0
        self.reverse = False

    def reverse_order(self):
        self.reverse = not self.reverse
    
    def next(self):
        i = self.index_current_player
        if not self.reverse:
            i += 1
        else:
            i -= 1
            i += len(self.players) # Prevent i from becoming negative
        i %= len(self.players)
        self.index_current_player = i
    
    @property
    def current_player(self):
        return self.players[self.index_current_player]
    

class CannotDraw(Exception):
    pass


class Board:
    def __init__(self, drawdeck: Deck, playdeck: Deck, players: PlayerGroup) -> None:
        self.drawdeck = drawdeck
        self.playdeck = playdeck
        self.players = players

    @property
    def top_card(self):
        return self.playdeck.cards[-1]

    def check(self, index):
        player = self.players.current_player
        card = player.hand[index]
        topcard = self.playdeck[-1]
        return card.is_same_suit(topcard) or card.is_same_value(topcard)

    def play(self, index: int):
        player = self.players.current_player
        card = player.hand.pop(index)
        self.playdeck.add(card)

    def next(self):
        self.players.next()

    def draw(self):
        drawdeck = self.drawdeck
        playdeck = self.playdeck
        if len(drawdeck) + len(playdeck) < 2:
            raise CannotDraw("Not enough cards on the board to draw one")
        # Reshuffle if drawdeck is empty
        if drawdeck.is_empty():
            topcard = playdeck.take()
            while(len(playdeck) > 0):
                card = playdeck.take()
                drawdeck.add(card)
            drawdeck.shuffle()
            playdeck.add(topcard)
        card = drawdeck.take()
        self.players.current_player.give_card(card)

def create_board(names):
    player_list = [Player(name) for name in names]
    players = PlayerGroup(player_list)
    playdeck = Deck([])
    drawdeck = create_full_deck()
    for player in players.players:
        for _ in range(8):
            player.give_card(drawdeck.take())
    playdeck.add(drawdeck.take())
    board = Board(drawdeck, playdeck, players)
    return board

# class Pesten:
#     def __init__(self, board: Board, interface: PestenInterface) -> None:
#         self.board = board # The board contains all the data about the game
#         self.interface = interface

#     async def start(self):
#         board = self.board
#         interface = self.interface
#         while(True):
#             index = await interface.get_choose(board)
#             if not board.check(index):
#                 await interface.invalid_card_choosen(board)
#                 continue
#             board.play(index)
#             board.next()


# def create_new_game(names, interface):
#     drawdeck = create_full_deck()
#     drawdeck.shuffle()
#     playdeck = Deck([])
#     playdeck.add(drawdeck.take())
#     players = [Player(name) for name in names]
#     player_group = PlayerGroup(players)
#     board = Board(drawdeck, playdeck, player_group)
#     for i in range(4):
#         for j in range(8):
#             board.draw()
#         board.next()
#     game = Pesten(board, interface)
#     return game


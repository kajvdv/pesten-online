import pytest

from pesten import create_board, Board, PlayerGroup, Deck, Player, Card, CannotDraw

TWO_OF_HEARTS = Card('hearts', 'two')
THREE_OF_HEARTS = Card("hearts", 'three')
FOUR_OF_HEARTS = Card('hearts', 'four')
THREE_OF_DIAMONDS = Card('diamonds', 'three')


def test_construct_board():
    board = create_board(['kaj', 'soy'])
    assert type(board) == Board
    assert board.playdeck
    for player in board.players.players:
        assert player.hand


def test_play_board():
    drawdeck = Deck()
    playdeck = Deck(FOUR_OF_HEARTS)
    players = PlayerGroup(
        Player("player1", TWO_OF_HEARTS, THREE_OF_DIAMONDS),
        Player("player2", THREE_OF_HEARTS, Card("not", "important"))
    )
    board = Board(drawdeck, playdeck, players)
    board.play_turn(0)
    assert board.players.index_current_player == 1
    board.play_turn(0)
    assert board.players.index_current_player == 0
    board.play_turn(0)
    assert board.players.index_current_player == 0
    assert board.has_won()


def test_shuffle_deck_two_cards():
    deck = Deck(TWO_OF_HEARTS, THREE_OF_HEARTS)
    deck.shuffle()
    assert deck.cards == [THREE_OF_HEARTS, TWO_OF_HEARTS]


def test_shuffle_deck_one_card():
    deck = Deck(TWO_OF_HEARTS)
    deck.shuffle()
    assert deck.cards == [TWO_OF_HEARTS]


def test_shuffle_deck_three_cards():
    deck = Deck(TWO_OF_HEARTS, THREE_OF_HEARTS, THREE_OF_DIAMONDS)
    deck.shuffle()
    assert deck.cards == [THREE_OF_DIAMONDS, TWO_OF_HEARTS, THREE_OF_HEARTS]


def test_draw_card():
    drawdeck = Deck(THREE_OF_DIAMONDS, THREE_OF_HEARTS)
    playdeck = Deck(FOUR_OF_HEARTS, TWO_OF_HEARTS)
    players = PlayerGroup(
        Player("player1", Card("not", "important")),
        Player("player2", Card("not", "important"))
    )
    board = Board(drawdeck, playdeck, players)
    assert board.top_card == TWO_OF_HEARTS
    board.play_turn(-1)
    assert board.players.index_current_player == 1
    board.play_turn(-1)
    assert board.players.index_current_player == 0
    board.play_turn(-1)
    assert board.players.index_current_player == 1


def test_cannot_draw():
    drawdeck = Deck(THREE_OF_DIAMONDS)
    playdeck = Deck(FOUR_OF_HEARTS)
    players = PlayerGroup(
        Player("player1", Card("not", "important")),
        Player("player2", Card("not", "important"))
    )
    board = Board(drawdeck, playdeck, players)
    board.play_turn(-1)
    assert board.players.index_current_player == 1
    with pytest.raises(CannotDraw):
        board.play_turn(-1)
    assert board.players.index_current_player == 1
    
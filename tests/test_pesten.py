from pesten.game import create_board, Board, PlayerGroup, Deck, Player, Card

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
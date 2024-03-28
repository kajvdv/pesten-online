from pesten.game import create_board, Board


def test_construct_board():
    board = create_board(['kaj', 'soy'])
    assert type(board) == Board
    assert board.playdeck
    for player in board.players.players:
        assert player.hand
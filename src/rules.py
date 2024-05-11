from typing import Protocol
from pesten import Board, Card


class PestenCard(Protocol):
    def check(self, game, index): ...
    def play(self, game, index: int): ...
    def next(self, game): ...
    def draw(self, game): ...


class DefaultPestenCard:
    def check(self, game, index):
        return game.check()
    
    def play(self, game, index: int):
        game.play(index)
    
    def next(self, game):
        game.next()

    def draw(self, game):
        game.draw()


class Pesten:
    def __init__(self, board: Board, rules: dict[Card, PestenCard]) -> None:
        self.board = board
        self.rules = rules
        self.default_rule = DefaultPestenCard()

    def play_turn(self, index: int):
        pesten_card = self.rules.get(self.board.top_card, self.default_rule)
        if index == -1:
            pesten_card.draw(self.board)
        elif pesten_card.check(self.board, index):
            pesten_card.play(self.board, index)
        else:
            return
        if not self.has_won():
            pesten_card.next(self.board)


# Implementation of the rules

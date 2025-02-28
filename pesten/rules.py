from typing import Protocol


def drawCards(game, choose):
    if game.check(choose):
        game.play(choose)
        game.next()
        # The next player has to draw two cards
        game.draw()
        game.draw()

def anotherTurn(game, choose):
    if game.check(choose):
        game.play(choose)

def skipTurn(game, choose):
    if game.check(choose):
        game.play(choose)
        game.next()
        game.next()

def reverseOrder(game, choose):
    if game.check(choose):
        game.play(choose)
        game.reverse = not game.reverse
        game.next()


def changeSuit(game, choose):
    if game.check(choose):
        game.play(choose)
        game.change_suit_state = "asking"


RULES_NAMES = {
    "Nog een keer": anotherTurn,
    "Kaart pakken": drawCards,
    "Suit uitkiezen": changeSuit,
    "Volgende speler beurt overslaan": skipTurn,
    "Spelvolgorde omdraaien": reverseOrder
}
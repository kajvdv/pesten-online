//TODO: Make modules of javascript files
let game = {
    canDraw: false,
    topCard: null,
    hand: [],
}
// Query elements
drawDeck = document.querySelector('.drawdeck')
topCard = document.querySelector("#topcard")
hand = document.querySelector('.hand')


// Define interface
function cardNames(card) {
    return "cards/" + card.value + "_of_" + card.suit + ".png"
}

drawDeck.addEventListener('click', onDraw)

function renderBoard(game) {
    if (game.canDraw) {
        drawDeck.setAttribute('src', 'cards/back.png')
    } else {
        drawDeck.setAttribute('src', 'cards/null.png')
    }
    
    topCard.setAttribute('src', cardNames(game.topCard))

    hand.innerHTML = ""
    game.hand.forEach(card => {
        const cardElement = document.createElement('img')
        cardElement.classList.add('card')
        cardElement.src = cardNames(card)
        cardElement.addEventListener('click', onSelect)
        hand.appendChild(cardElement)
    })
}

function setGame(newGame) {
    game = newGame
    renderBoard(game)
}

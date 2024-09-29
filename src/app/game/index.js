let websocket;
let gameId = ""
let currentPlayer = ""

suitMap = {
    "Schoppen": 'spades',
    "Harten": 'hearts',
    "Ruiten": 'diamonds',
    "Klaver": 'clubs',
}

valueMap = {
    "Twee": '2', "Drie": '3', "Vier": '4', "Vijf": '5', "Zes": '6', "Zeven": '7',
    "Acht": '8', "Negen": '9', "Tien": '10', "Boer": 'jack', "Vrouw": 'queen', "Heer": 'king', "Aas": 'ace'
}

function translateCard(serverCard) {
    const [suit, value] = serverCard.split(" ")
    return {suit: suitMap[suit], value: valueMap[value]}
}

function onSelect(event) { // Will be called in game.js
    const [source] = event.target.src.split('/').slice(-1)
    console.log(source)
    let [value, suit] = source.split('_of_')
    suit = suit.split('.')[0]
    console.log(value, 'of', suit)
    game.hand.forEach((card, index) => {
        if (card.suit === suit && card.value === value){
            websocket.send(index+1)
        }
    })
}

function onDraw() {
    websocket.send(0)
}

async function createGame() {
    const response = await fetch('http://localhost:8000/', {
        method: 'POST'
    })
    gameId = Number(await response.text())
}

async function connect(token, lobby_id) {
    websocket = new WebSocket(`ws://${window.location.host}/api/lobbies/connect?lobby_id=${0}`)
    websocket.onmessage = function(event) {
        const message = JSON.parse(event.data)
        console.log("received message", message)
        console.log("message type", typeof(message))
        if (typeof(message) === "number") return
        if ('error' in message) {
            console.error(message.error)
            return
        }
        const game = {
            canDraw: message.can_draw,
            hand: message.hand,
            topCard: message.topcard,
        }
        setGame(game)
        currentPlayer = Number(message.currentPlayer)
        gameId = Number(message.playerId)
        const nameplate = document.querySelector('.nameplate')
        nameplate.textContent = message.player
    }
    websocket.onclose = function(event) {
        console.log("closing websocket")
        // window.location.href = `/static/lobbies/index.html` // Return on close?
    }
}
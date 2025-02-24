import { useMemo, useEffect, useRef, useState } from "react"
// import "./styles.css"
import "./cards.css"
import server, {getUser, connect} from "../server"


// class GameConnection {
//     constructor(lobby_id) {
//         this.websocket = new WebSocket(`ws://${window.location.host}/api/lobbies/connect?lobby_id=${lobby_id}`)
//     }

//     onReceive(messageHandler, errorHandler) {
//         this.websocket.addEventListener('message', event => {
//             const data = JSON.parse(event.data)
//             console.log(data)
//             if ('error' in data) {
//                 errorHandler(data.error)
//                 console.log(data.error)
//             } else {
//                 messageHandler(data)
//             }
//         })
//     }

//     send(index) {
//         this.websocket.send(index)
//     }
// }

const suits = ["hearts", "diamonds", "clubs", "spades"];
const values = {
  "2": 'two', "3": 'three', "4": 'four', "5": 'five', "6": 'six', "7": 'seven', "8": 'eight', "9": 'nine', "10": 'ten',
  "jack": 'jack', "queen": 'queen', "king": 'king', "ace": 'ace', 'mirror': 'mirror', 'joker': 'joker'
};


function Card({card, onClick}) {
    const cardClass = values[card.value.toLowerCase()] + "_of_" + card.suit.toLowerCase()
    return <img className={"card" + " " + cardClass} onClick={() => onClick(card)} src='/game/cards/null.png'/>
}


function DrawDeck({onClick}) {
    return <img onClick={onClick} className="card card-back drawdeck" src="game/cards/null.png"/>
}


function useUser() {
    const [user, setUser] = useState("")
    useEffect(() => {
        getUser()
            .then(user => setUser(user))
    }, [])
    return user
}

function useConnection(lobby_id, onMessage, onError) {
    const serverConnection = useRef()
    useEffect(() => {
        console.log("Mounting useConnection")
        connect(lobby_id)
            .then(connection => {
                connection.onReceive(onMessage, onError)
                serverConnection.current = connection
            })
        return _ => {
            console.log("Cleaning up websocket")
            if (!serverConnection.current) return
            console.log("Calling close")
            serverConnection.current.close()
        }
    }, [])

    function playCard(index) {
        serverConnection.current.send(index)
    }

    function drawCard() {
        console.log('drawing')
        serverConnection.current.send(-1)
    }

    return [playCard, drawCard]
}


function ChooseSuit({visible, onChoose}) {
    
    return (<>
        <div className={"modal-overlay" + (visible ? " visible" : "")}></div>
        {visible ? <div className="choose-suit-modal">
            {['hearts', 'diamonds', 'spades', 'clubs'].map((suit, index) => 
                <Card onClick={() => onChoose(index)} card={{value: 'mirror', suit: suit}}/>
            )}
        </div> : null}
    </>)
}


function ErrorModal({visible, error}) {
    return (
        <>
            {visible ? <div className="error-modal">
                {error}
            </div> : null}
        </>
    )
}


function getGameName() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('lobby_id');
}


function Rule({cardValue, rule}) {
    return (
        <div className="rule">
            <Card card={{value: cardValue, suit: 'diamonds'}}/>
            <div className="rule-description">{rule.replace('_', " ")}</div>
        </div>
    )
}


function RuleShower() {
    const [extend, setExtend] = useState(false)
    const [rules, setRules] = useState({})
    const gameName = useMemo(getGameName, [])

    useEffect(_ => {
        server.get(`/lobbies/${gameName}/rules`)
            .then(response => {
                setRules(response.data)
            })
    }, [])

    return (
        <div className={"drawer" + (extend ? " extend" : "")}>
            <div className="handle">
                <img src="arrows-reverse.png" style={{"display": !extend ? "none" : ""}} className="handle" onClick={_ => setExtend(e => !e)}></img>
                <img src="arrows.png" style={{"display": extend ? "none" : ""}} className="handle" onClick={_ => setExtend(e => !e)}></img>
            </div>
            <div className="drawer-container">
                {Object.entries(rules).map(([cardValue, rule]) => <Rule cardValue={cardValue} rule={rule}/>)}
            </div>
        </div>
    )
}


function GamePage() {
    const params = new URLSearchParams(window.location.search)
    const lobby_id = params.get("lobby_id")
    const user = useUser()
    const [game, setGame] = useState()
    const [showError, setShowError] = useState(false)
    const [error, setError] = useState("")
    const [playCard, drawCard] = useConnection(lobby_id, setGame, setError)
    const [otherHandCounts, setOtherHandCounts] = useState({})

    useEffect(_ => {
        setShowError(error != "")
        if (error == '') return
        if (error.includes("Lost connection")) return
        setTimeout(_ => {
            setError("")
        }, 2000)
    }, [error])

    const gameWon = game?.message.includes('has won the game')
    useEffect(() => {
        if (!gameWon) return
        setError("")
    }, [gameWon])

    let otherHands = {...game?.otherPlayers} || {'': 0}
    delete otherHands[user]
    otherHands = Object.entries(otherHands)

    const emptySpot = <img className="card" src="game/cards/null.png" onClick={drawCard}/>
    const upsideDown = <img className="card card-back" src="game/cards/null.png"/>

    let playerIndex = -1
    let ownIndex = -1
    if (game) {
        const playerNames = Object.keys(game.otherPlayers)
        playerIndex = playerNames.indexOf(game.current_player)
        ownIndex = playerNames.indexOf(user)
        playerIndex = (playerIndex - ownIndex + playerNames.length) % playerNames.length
    }

    // Define css-classes for every playercount possibility
    let classNames = []
    if (otherHands.length <= 1) {
        classNames = ['player-position-1']
    } else if (otherHands.length === 2) {
        classNames = ['player-position-9', 'player-position-11']
    } else if (otherHands.length === 3) {
        classNames = ['player-position-2', 'player-position-1', 'player-position-3']
    } else if (otherHands.length === 4) {
        classNames = ['player-position-8', 'player-position-9', 'player-position-11', 'player-position-12']
    } else if (otherHands.length === 5) {
        classNames = ['player-position-8', 'player-position-9', 'player-position-10', 'player-position-11', 'player-position-12']
    }

    const playdeck = game?.topcard.value == 'mirror' ? (
        <>
            {emptySpot}
            <div className="playdeck">
                {game?.topcard ? <Card onClick={() => {}} card={game.previous_topcard}/> : emptySpot}
                {game?.topcard ? <Card onClick={() => {}} card={game.topcard}/> : emptySpot}
            </div>
        </>
    ) : game?.topcard ? <Card onClick={() => {}} card={game.topcard}/> : emptySpot

    return (
        <div className="ground">
            <div className="board">
                <div id="nameplate">
                    <div className="board-message">{game?.message}</div>
                    {gameWon ? <a href='/lobbies'>Go back to lobbies</a> : null}
                </div>
                {otherHands.map((hand, index) => <div className={classNames[index] + (index === playerIndex-1 ? " current" : "")}>
                    <div className="player-name">{hand[0]}</div>
                    <div className={"player"}>
                        {Array(hand[1]).fill(upsideDown)}
                    </div>
                </div>)}
                <div className={"middle" + (playerIndex > -1 ? " indicator" + playerIndex : "")}>
                    {game?.can_draw ? <DrawDeck onClick={drawCard}/> : emptySpot}
                    {playdeck}
                </div>
                {game?.draw_count > 0 ? <div className="draw-counter">
                    {game.draw_count}
                </div> : null}
                <div className={"hand" + (0 === playerIndex ? " current" : "")}>
                    <div className="player-name">{user}</div>
                    <div className={"player"}>
                        {game?.hand.map((card, index) => <Card
                            key={card.value == 'joker' ? card.suit + card.value + index : card.suit + card.value}
                            card={card}
                            onClick={_ => playCard(index)}
                        />)}
                    </div>
                </div>
                <ChooseSuit visible={game?.choose_suit && ownIndex == playerIndex} onChoose={index => playCard(index)}/>
                <ErrorModal visible={showError && !gameWon} error={error}/>
                <RuleShower/>
            </div>
        </div>
    )
}

export default GamePage
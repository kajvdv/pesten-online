import { useEffect, useRef, useState } from "react"
import "./styles.css"
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


function Card({card, onClick}) {
    const src = "/game/cards/" + card.value.toLowerCase() + "_of_" + card.suit.toLowerCase() + ".png"
    
    return <img className="card" onClick={() => onClick(card)} src={src}/>
}


function DrawDeck({onClick}) {
    return <img onClick={onClick} className="card drawdeck" src="game/cards/back.png"/>
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
        // const websocket = new WebSocket(`ws://${window.location.host}/api/lobbies/connect?lobby_id=${lobby_id}`)
        // websocket.addEventListener('message', event => {
        //     const data = JSON.parse(event.data)
        //     console.log(data)
        //     if ('error' in data) {
        //         onError(data.error)
        //         console.log(data.error)
        //     } else {
        //         onReceive(data)
        //     }
        // })
        console.log(server)
        connect(lobby_id)
            .then(connection => {
                console.log(connection)
                connection.onReceive(onMessage, onError)
                serverConnection.current = connection
            })
    }, [])

    function playCard(card, index) {
        console.log(card, index)
        serverConnection.current.send(index)
    }

    function drawCard() {
        console.log('drawing')
        serverConnection.current.send(0)
    }
    return [playCard, drawCard]
}

function GamePage() {
    const params = new URLSearchParams(window.location.search)
    const lobby_id = params.get("lobby_id")
    const user = useUser()
    const [game, setGame] = useState()
    const [error, setError] = useState("")
    const [playCard, drawCard] = useConnection(lobby_id, setGame, setError)
    const [otherHandCounts, setOtherHandCounts] = useState({})

    // useEffect(() => {
    //     if (!game) return
    //     console.log(game)
    // }, [game])

    let otherHands = game?.otherPlayers || {'': 0}
    delete otherHands[user]
    console.log(Object.entries(otherHands))
    otherHands = Object.entries(otherHands)

    const emptySpot = <img className="card" src="game/cards/null.png"/>
    const upsideDown = <img className="card" src="game/cards/back.png"/>

    let classNames = []
    if (otherHands.length <= 1) {
        classNames = ['topplayer']
    } else {
        classNames = ['leftplayer', 'topplayer', 'rightplayer']
    }
    
    return (
        <div className="board">
            <div id="nameplate">
                {user}
                <div className="board-message">{game?.message}</div>
                {game?.message.includes('has won the game') ? <a href='/lobbies'>Go back to lobbies</a> : null}
            </div>
            {otherHands.map((hand, index) => <div className={classNames[index]}>
                {Array(hand[1]).fill(upsideDown)}
            </div>)}
            <div className="middle">
                {game?.can_draw ? <DrawDeck onClick={drawCard}/> : emptySpot}
                {game?.topcard ? <Card onClick={() => {}} card={game.topcard}/> : emptySpot}
            </div>
            <div className="hand">
                {game?.hand.map((card, index) => <Card key={card.suit + card.value} card={card} onClick={card => playCard(card, index+1)}/>)}
            </div>
        </div>
    )
}

export default GamePage
import { useEffect, useRef, useState } from "react"
import "./styles.css"
import server from "../server"


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


function UpsideDown({onClick}) {
    return <img onClick={onClick} className="card" src="game/cards/back.png"/>
}


function useUser() {
    const [user, setUser] = useState("")
    useEffect(() => {
        server.getUser()
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
        server.connect(lobby_id)
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
    const user = useUser()
    const [game, setGame] = useState()
    const [error, setError] = useState("")
    const [playCard, drawCard] = useConnection(0, setGame, setError)

    const emptySpot = <img className="card" src="game/cards/null.png"/>
    const upsideDown = <img className="card" src="game/cards/back.png"/>

    return (
        <div className="board">
            <div id="nameplate">{user}</div>
            <div className="topplayer">{[
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
            ]}</div>
            <div className="leftplayer">{[
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
            ]}</div>
            <div className="rightplayer">{[
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
                upsideDown,
            ]}</div>
            <div className="middle">
                {game?.can_draw ? <UpsideDown onClick={drawCard}/> : emptySpot}
                {game?.topcard ? <Card onClick={() => {}} card={game.topcard}/> : emptySpot}
            </div>
            <div className="hand">
                {game?.hand.map((card, index) => <Card key={card.suit + card.value} card={card} onClick={card => playCard(card, index+1)}/>)}
            </div>
        </div>
    )
}

export default GamePage
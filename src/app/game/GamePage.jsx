
import { useEffect, useRef, useState } from "react"
import "./styles.css"
import server from "../server"


function Card({card, onClick}) {
    const src = "/game/cards/" + card.value.toLowerCase() + "_of_" + card.suit.toLowerCase() + ".png"
    
    return <img className="card" onClick={() => onClick(card)} src={src}/>
}


// function EmptySpot() {
//     return <img className="card" src="game/cards/null.png"/>
// }

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

function useConnection(lobby_id, onReceive) {
    const server = useRef()
    useEffect(() => {
        const websocket = new WebSocket(`ws://${window.location.host}/api/lobbies/connect?lobby_id=${lobby_id}`)
        websocket.addEventListener('message', event => {
            const data = JSON.parse(event.data)
            console.log(data)
            if ('error' in data) {
                console.log(data.error)
            } else {
                onReceive(data)
            }
        })
        server.current = websocket
    }, [])

    function playCard(card, index) {
        console.log(card, index)
        server.current.send(index)
    }

    function drawCard() {
        console.log('drawing')
        server.current.send(0)
    }
    return [playCard, drawCard]
}

function GamePage() {
    const user = useUser()
    const [game, setGame] = useState()
    const [playCard, drawCard] = useConnection(0, setGame)

    const emptySpot = <img className="card" src="game/cards/null.png"/>
    const upsideDown = <img className="card" src="game/cards/back.png"/>

    return (
        <div className="board">
            <div className="nameplate">{user}</div>
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
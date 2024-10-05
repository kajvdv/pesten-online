
import { useEffect, useState } from "react"
import "./styles.css"
import server from "../server"

const suitMap = {
    "Schoppen": 'spades',
    "Harten": 'hearts',
    "Ruiten": 'diamonds',
    "Klaver": 'clubs',
}

const valueMap = {
    "Twee": '2', "Drie": '3', "Vier": '4', "Vijf": '5', "Zes": '6', "Zeven": '7',
    "Acht": '8', "Negen": '9', "Tien": '10', "Boer": 'jack', "Vrouw": 'queen', "Heer": 'king', "Aas": 'ace'
}


function Card({card}) {
    const src = "/game/cards/" + card.value.toLowerCase() + "_of_" + card.suit.toLowerCase() + ".png"
    return <img className="card" src={src}/>
}


function EmptySpot() {
    return <img className="card" src="game/cards/null.png"/>
}

function translateServer(serverCard) {
    const [suit, value] = serverCard.split(" ")
    return {suit: suitMap[suit], value: valueMap[value]}
}


function useUser() {
    const [user, setUser] = useState("")
    useEffect(() => {
        server.getUser()
            .then(user => setUser(user))
    }, [])
    return user
}



function GamePage() {
    const user = useUser()
    const [game, setGame] = useState()

    useEffect(() => {
        const lobby_id = 0
        const websocket = new WebSocket(`ws://${window.location.host}/api/lobbies/connect?lobby_id=${lobby_id}`)
        websocket.addEventListener('message', event => {
            const data = JSON.parse(event.data)
            console.log(data)
            setGame(data)
        })


    }, [])

    return (
        <div className="board">
            <div className="nameplate">{user}</div>
            <div className="middle">
                <EmptySpot/>
                <EmptySpot/>
            </div>
            <div className="hand">
                {game?.hand.map(card => <Card card={card}/>)}
                {/* <img className="card" src="game/cards/ace_of_clubs.png" alt=""/>
                <img className="card" src="game/cards/ace_of_diamonds.png" alt=""/>
                <img className="card" src="game/cards/ace_of_hearts.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/>
                <img className="card" src="game/cards/ace_of_spades.png" alt=""/> */}
            </div>
        </div>
    )
}

export default GamePage
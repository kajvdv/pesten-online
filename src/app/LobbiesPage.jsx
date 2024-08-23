import { useState } from "react"
import { Link } from "react-router-dom"
import './LobbiesPage.css'


function Lobby(props) {
    console.log(props)
    return <Link className="lobby">
        Join game
    </Link>
}


function LobbiesPage() {
    const [lobbies, setLobbies] = useState([])
    async function createLobby(event) {
        try {
            const response = await fetch('/api/lobbies', {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                },
                body: '{"size":2}'
            })

            if (!response?.ok) {
                throw new Error("Response not ok")
            }
            setLobbies(lobbies => [...lobbies, newLobby])
        } catch {
            console.error("Failed to create a new lobby")
        }
    }
    return <>
        <header>Lobbies</header>
        <div className="lobbies">
            <div id="lobby-list">
                {lobbies.map((lobby, i) => <Lobby key={i} {...lobby}/>)}
            </div>
            <button id="new-lobby-button" onClick={createLobby}>Create new</button>
        </div>
    </>
}

export default LobbiesPage
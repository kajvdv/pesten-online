import { useContext, useState, useEffect } from "react"
import { Link } from "react-router-dom"
import './LobbiesPage.css'
import { AuthContext } from "./AuthProvider"


function Lobby({size, creator}) {
    useEffect(() => {
        console.log(size, creator)

    }, [])
    return <Link className="lobby">
        Join game
    </Link>
}


function LobbiesPage() {
    const [lobbies, setLobbies] = useState([])
    const [accessToken, setAccessToken] = useContext(AuthContext)
    const [creating, setCreating] = useState(false)
    useEffect(() => {
        if (!creating) return;
        fetch('/api/lobbies', {
            method: 'POST',
            headers: {
                "Authorization": accessToken,
                "Content-Type": "application/json",
            },
            body: '{"size":2}'
        }).then(response => {
            if (!response?.ok) {
                response.reject("Response not ok")
            }
            return response.json()
        }).then(newLobby => {
            console.log(newLobby)
            setLobbies(lobbies => [...lobbies, newLobby])
            setCreating(false)
        })
    }, [creating])

    useEffect(() => {
        const abortController = new AbortController()
        fetch("/api/lobbies", {
            signal: abortController.signal,
            method: 'get',
            headers: {
                "Authorization": accessToken,
                "Content-Type": "application/json",
            },
        }).then(response => {
            return response.json()
        }).then(lobbies => {
            console.log("setting lobbies")
            setLobbies(lobbies)
        }).catch(error => {
            console.error(error)
        })
        return () => {
            // Cancel get lobbies request
            abortController.abort("LobbiesPage is unmounting, canceling request")
        }
    }, [])
    
    return <>
        <header>Lobbies</header>
        <div className="lobbies">
            <div id="lobby-list">
                {lobbies.map((lobby, i) => <Lobby key={i} {...lobby}/>)}
            </div>
            <button id="new-lobby-button" onClick={() => setCreating(true)}>Create new</button>
        </div>
    </>
}

export default LobbiesPage
import { useContext, useState, useEffect, createContext, useRef } from "react"
import { Link, useAsyncError } from "react-router-dom"
import './LobbiesPage.css'
import { AuthContext } from "./AuthProvider"


const LobbiesContext = createContext()


async function postLobby(size, accessToken) {
    const response = await fetch('/api/lobbies', {
        method: 'POST',
        headers: {
            "Authorization": accessToken,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({size: size})
    })
    if (!response.ok) {
        throw new Error("Failed to create a lobby")
    }
    return response.json()
}


function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])
    const [accessToken, setAccessToken] = useContext(AuthContext)


    async function getLobbies() {
        const response = await fetch("/api/lobbies", {
            method: 'get',
            headers: {
                "Authorization": accessToken,
                "Content-Type": "application/json",
            },
        })
        setLobbies(await response.json())
    }

    async function createLobby(size) {
        const lobbies = await postLobby(size, accessToken)
        setLobbies(lobbies)
    }

    async function deleteLobby(id) {
        const response = await fetch(`/api/lobbies?id=${id}`, {
            method: 'delete',
        })
        setLobbies(await response.json())
    }
    
    useEffect(() => {
        getLobbies()
    }, [])


    return <LobbiesContext.Provider value={{lobbies, getLobbies, createLobby, deleteLobby}}>
        {children}
    </LobbiesContext.Provider>
}


function Lobby({id, size, creator}) {
    const lobbies = useContext(LobbiesContext)
    const [deleting, setDeleting] = useState(false)
    useEffect(() => {
        if (!deleting) return
        lobbies.deleteLobby(id)
    }, [deleting])
    return <>
        <Link className="lobby">
            Join game {id}
        </Link>
        <button onClick={() => setDeleting(true)}>Delete</button>
    </>
}


function LobbyList() {
    const lobbies = useContext(LobbiesContext)
    return <>
        <header>Lobbies</header>
        <div className="lobbies">
            <div id="lobby-list">
                {lobbies.lobbies.map((lobby, i) => <Lobby key={lobby.id} {...lobby}/>)}
            </div>
            <button id="new-lobby-button" onClick={() => lobbies.createLobby(2)}>Create new</button>
        </div>
    </>
}


function LobbiesPage() {
    
    
    return <LobbiesProvider>
        <LobbyList/>
    </LobbiesProvider>
}

export default LobbiesPage
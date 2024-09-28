import { useContext, useState, useEffect, createContext, useRef } from "react"
import { Link, useAsyncError } from "react-router-dom"
import './LobbiesPage.css'
import { AuthContext } from "./AuthProvider"
import server from "./server"


const LobbiesContext = createContext()


function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])

    async function getLobbies() {
        const lobbies = await server.getLobbies()
        setLobbies(lobbies)
    }

    async function createLobby(size) {
        const lobbies = await server.postLobby(size)
        setLobbies(lobbies)
    }

    async function deleteLobby(id) {
        const lobbies = await server.deleteLobby(id)
        setLobbies(lobbies)
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
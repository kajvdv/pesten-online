import { useContext, useState, useEffect, createContext, useRef } from "react"
import './LobbiesPage.css'
import server from "../server"


const LobbiesContext = createContext()


function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])

    async function getLobbies() {
        const lobbies = await server.getLobbies()
        setLobbies(lobbies)
    }

    async function createLobby(size, creator) {
        const lobby = await server.postLobby(size, creator)
        setLobbies(lobbies => [...lobbies, lobby])
    }

    async function deleteLobby(id) {
        const deletedLobby = await server.deleteLobby(id)
        setLobbies(lobbies => lobbies.filter(lobby => lobby.id !== deletedLobby.id))
    }
    
    useEffect(() => {
        getLobbies()
    }, [])


    return <LobbiesContext.Provider value={{lobbies, getLobbies, createLobby, deleteLobby}}>
        {children}
    </LobbiesContext.Provider>
}


function Lobby({id, size, capacity, creator, user}) {
    const lobbies = useContext(LobbiesContext)
    const [deleting, setDeleting] = useState(false)

    useEffect(() => {
        if (!deleting) return
        lobbies.deleteLobby(id)
            .then(() => setDeleting(false))
    }, [deleting])

    function join() {
        window.location.href = "/game?lobby_id=" + id
    }

    return <div className="lobby">
        <h1 className="lobby-join">Game {id}</h1>
        <div>Created by {creator}</div>
        <div>{size} / {capacity}</div>
        {user == creator ? <button className='lobby-delete-button' onClick={() => setDeleting(true)}>{!deleting ? "Delete" : "Deleting..."}</button> : null}
        <button onClick={join}>Join</button>
    </div>
}


function LobbyList() {
    const lobbies = useContext(LobbiesContext)
    const [userName, setUserName] = useState("")

    useEffect(() => {
        server.getUser()
            .then(userName => setUserName(userName))
    }, [])

    return <>
        <header>Lobbies of {userName}</header>
        <div className="lobbies">
            <div id="lobby-list">
                {lobbies.lobbies.map((lobby, i) => <Lobby key={lobby.id} {...lobby} user={userName}/>)}
            </div>
            <button id="new-lobby-button" onClick={() => lobbies.createLobby(2, userName)}>Create new game</button>
        </div>
    </>
}


function LobbiesPage() {
    
    
    return <LobbiesProvider>
        <LobbyList/>
    </LobbiesProvider>
}

export default LobbiesPage
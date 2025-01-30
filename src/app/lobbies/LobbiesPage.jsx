import { useContext, useState, useEffect, createContext, useRef } from "react"
import './LobbiesPage.css'
import server from "../server"


const LobbiesContext = createContext()


function CreateLobbyModal({onCancel, defaultGameName}) {
    const lobbies = useContext(LobbiesContext)

    return (
        <form className="create-modal" onSubmit={async event => {
                event.preventDefault()
                const name = event.target[0].value
                const count = event.target[1].value
                const aiCount = event.target[2].value
                await lobbies.createLobby(name, count, aiCount)
                onCancel()
        }}>
            <input type="text" defaultValue={defaultGameName}></input>
            {/* TODO: Make sure that player cannot choose too many AI's */}
            <input type="number" min="2" max="6" defaultValue={2}></input>
            <input type="number" min="0" max="5" defaultValue={0}></input>
            <button type="submit">Create</button>
            <button onClick={onCancel}>Cancel</button>
        </form>
    )
}


function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])

    async function getLobbies() {
        const lobbies = await server.getLobbies()
        setLobbies(lobbies)
    }

    async function createLobby(name, size, aiCount) {
        const lobby = await server.postLobby(name, size, aiCount)
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


function Lobby({id, size, capacity, creator, user, players}) {
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

    return <div className="lobby" style={players.includes(user) ? {backgroundColor: 'yellow'} : {}}>
        <h1 className="lobby-join">{id}</h1>
        <div>Created by {creator}</div>
        <div>{size} / {capacity}</div>
        {user == creator ? <button className='lobby-delete-button' onClick={() => setDeleting(true)}>{!deleting ? "Delete" : "Deleting..."}</button> : null}
        <button onClick={join}>Join</button>
    </div>
}


function LobbyList() {
    const lobbies = useContext(LobbiesContext)
    const [userName, setUserName] = useState("")
    const [showModal, setShowModal] = useState(false)

    useEffect(() => {
        server.getUser()
            .then(userName => setUserName(userName))
    }, [])

    useEffect(() => {
        console.log("showing modal")
    }, [showModal])

    return <>
        <header>Lobbies of {userName}</header>
        <div className="lobbies">
            <div id="lobby-list">
                {lobbies.lobbies.map((lobby, i) => <Lobby key={lobby.id} {...lobby} user={userName}/>)}
            </div>
            <div className="lobby-buttons">
                <button className="new-lobby-button" onClick={() => setShowModal(true)}>Create new game</button>
            </div>
            {showModal ? <CreateLobbyModal
                onCancel={() => setShowModal(false)}
                defaultGameName={userName + "'s game"}
            /> : null}
        </div>
    </>
}


function LobbiesPage() {
    
    
    return <LobbiesProvider>
        <LobbyList/>
    </LobbiesProvider>
}

export default LobbiesPage
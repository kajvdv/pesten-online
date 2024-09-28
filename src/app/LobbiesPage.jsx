import { useContext, useState, useEffect, createContext, useRef } from "react"
import { Link, useAsyncError } from "react-router-dom"
import './LobbiesPage.css'
import { AuthContext } from "./AuthProvider"


const LobbiesContext = createContext()


async function getLobbies(accessToken) {
    const response = await fetch("/api/lobbies", {
        method: 'get',
        headers: {
            "Authorization": accessToken,
            "Content-Type": "application/json",
        },
    })
    if (!response.ok) {
        return Promise.reject(response.text)
    }
    return response.json()
}


async function postLobby(size, accessToken) {
    fetch('/api/lobbies', {
        method: 'POST',
        headers: {
            "Authorization": accessToken,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({size: size})
    })
        .then(response => {
            if (!response?.ok) {
                return response.reject("Response not ok")
            }
            return response.json()
        })
}


function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])
    const [fetching, setFetching] = useState(true)
    const [accessToken, setAccessToken] = useContext(AuthContext)

    useEffect(() => {
        if (!fetching) return
        getLobbies(accessToken)
            .then(lobbies => {
                console.log("setting lobbies")
                console.log(lobbies)
                setLobbies(lobbies)
            })
            .catch(error => {
                console.error(error)
            })
            .finally(() => {
                setFetching(false)
            })
    }, [fetching])

    function fetchLobbies() {
        setFetching(true)
    }

    return <LobbiesContext.Provider value={[lobbies, fetchLobbies]}>
        {children}
    </LobbiesContext.Provider>
}

function useLobbies() {
    const [lobbies, fetchLobbies] = useContext(LobbiesContext)
    const [posting, setPosting] = useState(false)
    const [deleting, setDeleting] = useState(false)
    const [accessToken, setAccessToken] = useContext(AuthContext)


    const postingSize = useRef()
    useEffect(() => {
        if (!posting) return
        postLobby(postingSize, accessToken)
            .then(newLobby => {
                console.log(newLobby)
                fetchLobbies()
            })
            .finally(() => {
                setPosting(false)
            })
    }, [posting])

    const deleteId = useRef()
    useEffect(() => {
        if (!deleting) return
        fetch(`/api/lobbies?id=${deleteId.current}`, {
            method: 'delete',
        }).then(() => {
            fetchLobbies()
        }).finally(() => {
            setDeleting(false)
        })
    }, [deleting])
    
    function createLobby(size) {
        postingSize.current = size
        setPosting(true)
    }

    function deleteLobby(id) {
        deleteId.current = id
        setDeleting(true)
    }
    return {lobbies, fetchLobbies, createLobby, deleteLobby}
}

function Lobby({id, size, creator}) {
    const api = useLobbies()
    return <>
        <Link className="lobby">
            Join game
        </Link>
        <button onClick={() => api.deleteLobby(id)}>Delete</button>
    </>
}


function LobbyList() {
    const api = useLobbies()
    return <>
        <header>Lobbies</header>
        <div className="lobbies">
            <div id="lobby-list">
                {api.lobbies.map((lobby, i) => <Lobby key={i} {...lobby}/>)}
            </div>
            <button id="new-lobby-button" onClick={() => api.createLobby(2)}>Create new</button>
        </div>
    </>
}


function LobbiesPage() {
    
    
    return <LobbiesProvider>
        <LobbyList/>
    </LobbiesProvider>
}

export default LobbiesPage
import { useContext, useState, useEffect, createContext, useRef } from "react"
import { Link, useAsyncError } from "react-router-dom"
import './LobbiesPage.css'
import { AuthContext } from "./AuthProvider"

const LobbiesContext = createContext()

function LobbiesProvider({children}) {
    const [lobbies, setLobbies] = useState([])
    const [fetching, setFetching] = useState(false)
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
        }).finally(() => {
            setFetching(false)
        })

        return () => {
            // Cancel get lobbies request
            abortController.abort("LobbiesPage is unmounting, canceling request")
        }
    }, [])

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

    const postingSize = useRef()
    useEffect(() => {
        if (!posting) return
        fetch('/api/lobbies', {
            method: 'POST',
            headers: {
                "Authorization": accessToken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({size: postingSize.current})
        }).then(response => {
            if (!response?.ok) {
                response.reject("Response not ok")
            }
            return response.json()
        }).then(newLobby => {
            console.log(newLobby)
            fetchLobbies()
        }).finally(() => {
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
    
    function postLobby(size) {
        postingSize.current = size
        setPosting(true)
    }

    function deleteLobby(id) {
        deleteId.current = id
        setDeleting(true)
    }
    [lobbies, fetchLobbies, postLobby, deleteLobby]
}

function Lobby({id, size, creator}) {
    const [deleting, setDeleting] = useState(false)
    useEffect(() => {
        if (!deleting) return
        fetch(`/api/lobbies?id=${id}`, {
            method: 'delete',
        })
        setDeleting(false)
    }, [deleting])
    return <>
        <Link className="lobby">
            Join game
        </Link>
        <button onClick={() => setDeleting(true)}>Delete</button>
    </>
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
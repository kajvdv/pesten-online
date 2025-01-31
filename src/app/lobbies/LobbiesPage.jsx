import { useContext, useState, useEffect, createContext, useRef } from "react";
import "./LobbiesPage.css";
import server, { getUser } from "../server";

const LobbiesContext = createContext();

function CreateLobbyModal({ onCancel, defaultGameName }) {
    const lobbies = useContext(LobbiesContext);
    const modalRef = useRef(null);

    useEffect(() => {
        modalRef.current.style.opacity = 0;
        modalRef.current.style.transform = "translateY(-20px)";
        requestAnimationFrame(() => {
            modalRef.current.style.transition = "opacity 0.3s, transform 0.3s";
            modalRef.current.style.opacity = 1;
            modalRef.current.style.transform = "translateY(0)";
        });
    }, []);

    function handleClose() {
        modalRef.current.style.opacity = 0;
        modalRef.current.style.transform = "translateY(-20px)";
        setTimeout(onCancel, 300);
    }

    return (
        <form ref={modalRef} className="create-modal" onSubmit={async (event) => {
            event.preventDefault();
            const name = event.target[0].value;
            const count = event.target[1].value;
            const aiCount = event.target[2].value;
            await lobbies.createLobby(name, count, aiCount);
            handleClose();
        }}>
            <input type="text" defaultValue={defaultGameName}></input>
            <input type="number" min="2" max="6" defaultValue={2}></input>
            <input type="number" min="0" max="5" defaultValue={0}></input>
            <button type="submit">Create</button>
            <button type="button" onClick={handleClose}>Cancel</button>
        </form>
    );
}

function LobbiesProvider({ children }) {
    const [lobbies, setLobbies] = useState([]);

    async function getLobbies() {
        const response = await server.get("/lobbies");
        setLobbies(response.data);
    }

    async function createLobby(name, size, aiCount) {
        const response = await server.post("/lobbies", { name, size, aiCount });
        setLobbies((lobbies) => [...lobbies, response.data]);
    }

    async function deleteLobby(id) {
        const response = await server.delete(`/lobbies/${id}`);
        setLobbies((lobbies) => lobbies.filter((lobby) => lobby.id !== response.data.id));
    }

    useEffect(() => {
        getLobbies();
    }, []);

    return (
        <LobbiesContext.Provider value={{
            lobbies,
            getLobbies,
            createLobby,
            deleteLobby,
        }}>
            {children}
        </LobbiesContext.Provider>
    );
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
    const lobbies = useContext(LobbiesContext);
    const [userName, setUserName] = useState("");
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        getUser().then((userName) => setUserName(userName));
    }, []);

    return (
        <>
            <header>Lobbies of {userName}</header>
            <div className="lobbies">
                <div id="lobby-list">
                    {lobbies.lobbies.map((lobby) => (
                        <Lobby key={lobby.id} {...lobby} user={userName} />
                    ))}
                </div>
                <div className="lobby-buttons">
                    <button className="new-lobby-button" onClick={() => setShowModal(true)}>
                        Create new game
                    </button>
                </div>
                {showModal && (
                    <CreateLobbyModal
                        onCancel={() => setShowModal(false)}
                        defaultGameName={userName + "'s game"}
                    />
                )}
            </div>
        </>
    );
}

function LobbiesPage() {
    return (
        <LobbiesProvider>
            <LobbyList />
        </LobbiesProvider>
    );
}

export default LobbiesPage;

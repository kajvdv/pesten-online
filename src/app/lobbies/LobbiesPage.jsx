import { useContext, useState, useEffect, createContext, useRef } from "react";
import "./LobbiesPage.css";
import server, { getUser } from "../server";

const LobbiesContext = createContext();


function CardValuesDropDown({name}) {
    console.log("Rerendering", name)
    return (
        <select name={name}>
            {/* TODO: Change values to ints */}
            {/* TODO: Dynamically get rules from server */}
            <option value="Nog een keer">Nog een keer</option>
            <option value="Kaart pakken">Kaart pakken</option>
            <option value="Suit uitkiezen">Suit uitkiezen</option>
            <option value="Volgende speler beurt overslaan">Volgende speler beurt overslaan</option>
        </select>
    )
}


function RuleMapping({}) {
    const [cardValue, setCardValue] = useState("Twee")

    return (
        <div className="rule-mapping">
            <select onChange={e => setCardValue(e.target.value)}>
                <option value="2">Twee</option>
                <option value="3">Drie</option>
                <option value="4">Vier</option>
                <option value="5">Vijf</option>
                <option value="6">Zes</option>
                <option value="7">Zeven</option>
                <option value="8">Acht</option>
                <option value="9">Negen</option>
                <option value="10">Tien</option>
                <option value="J">Boer</option>
                <option value="Q">Koningin</option>
                <option value="K">Koning</option>
                <option value="A">Aas</option>
            </select>
            <CardValuesDropDown name={cardValue}/>
        </div>
    )
}



function CreateLobbyModal({ visible, onCancel, userName }) {
    const lobbies = useContext(LobbiesContext);
    const modalRef = useRef(null);

    const formElements = (
        <>
            <label htmlFor="gamename">Name of game</label>
            <input name="gamename" type="text" defaultValue={userName + "'s game"}></input>
            <label htmlFor="playercount">Amount of players</label>
            <input name="playercount" type="number" min="2" max="6" defaultValue={2}></input>
            <label htmlFor="aicount">Amount of AI's</label>
            <input name="aicount" type="number" min="0" max="5" defaultValue={0}></input>
            <h3>Speciale regels</h3>
            <div className="rule-mappings">
                <RuleMapping cardValue={2}/>
                <RuleMapping cardValue={3}/>
                <RuleMapping cardValue={4}/>
            </div>
            <div className="modal-buttons">
                <button type="button" onClick={onCancel}>Cancel</button>
                <button type="submit">Create</button>
            </div>
        </>
    )

    return (
        <div className={"create-modal" + (visible ? " visible" : "")}>
            <h1>Create a new game</h1>
            <form className="create-form" ref={modalRef} 
            onSubmit={async (event) => {
                event.preventDefault();
                await lobbies.createLobby(new FormData(event.target));
                onCancel();
            }}>
                {userName ? formElements : null}
            </form>
        </div>
    );
}

function LobbiesProvider({ children }) {
    const [lobbies, setLobbies] = useState([]);

    async function getLobbies() {
        const response = await server.get("/lobbies");
        setLobbies(response.data);
    }

    async function createLobby(form) {
        const response = await server.post("/lobbies", form);
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
    const [showModal, setShowModal] = useState(true);

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
                <CreateLobbyModal
                    visible={showModal}
                    onCancel={() => setShowModal(false)}
                    userName={userName}
                />
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

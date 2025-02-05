import { useContext, useState, useEffect, createContext, useRef } from "react";
import "./LobbiesPage.css";
import server, { getUser } from "../server";
import personOutline from "../../../public/9035563_person_outline_icon.svg";
import personFill from "../../../public/309035_user_account_human_person_icon.svg";


const LobbiesContext = createContext();


function RuleMapping({}) {
    const [cardValue, setCardValue] = useState("two")

    return (
        <div className="rule-mapping">
            <select onChange={e => setCardValue(e.target.value)}>
                <option value="two">Twee</option>
                <option value="three">Drie</option>
                <option value="four">Vier</option>
                <option value="five">Vijf</option>
                <option value="six">Zes</option>
                <option value="seven">Zeven</option>
                <option value="eight">Acht</option>
                <option value="nine">Negen</option>
                <option value="ten">Tien</option>
                <option value="jack">Boer</option>
                <option value="queen">Koningin</option>
                <option value="king">Koning</option>
                <option value="ace">Aas</option>
            </select>
            <select name={cardValue}>
                {/* TODO: Change values to ints */}
                {/* TODO: Dynamically get rules from server */}
                <option value="Nog een keer">Nog een keer</option>
                <option value="Kaart pakken">Kaart pakken</option>
                <option value="Suit uitkiezen">Suit uitkiezen</option>
                <option value="Volgende speler beurt overslaan">Volgende speler beurt overslaan</option>
            </select>
            <button type="button">Delete</button>
        </div>
    )
}


function RuleMappings({}) {
    const [ruleCount, setRuleCount] = useState(0)

    // TODO: Use card value as key instead of index
    // I'll have to decide if it is okay to put multiple rules on one card. Would be nice
    // If so, then the card value together with the rule should be the key
    const mappings = Array.from({length: ruleCount}, (_, i) => <RuleMapping key={i}/>)
    return (
        <div className="rule-mappings">
            {mappings}
            <button type="button" onClick={() => setRuleCount(val => val+1)}>Add New Rule</button>
        </div>
    )
}


function CreateLobbyModal({ visible, onCancel, userName }) {
    const lobbies = useContext(LobbiesContext);
    const modalRef = useRef(null);

    const formElements = (
        <>
            <label htmlFor="name">Name of game</label>
            <input name="name" type="text" defaultValue={userName + "'s game"}></input>
            <label htmlFor="size">Amount of players</label>
            <input name="size" type="number" min="2" max="6" defaultValue={2}></input>
            <label htmlFor="aiCount">Amount of AI's</label>
            <input name="aiCount" type="number" min="0" max="5" defaultValue={0}></input>
            <h3>Speciale regels</h3>
            <RuleMappings/>
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
        <div className="player-icons">
            {Array.from({length: size}).map(() => <img className="icon-person-fill" src={personFill} alt="person"></img>)}
            {Array.from({length: capacity - size}).map(() => <img className="icon-person-outline" src={personOutline} alt="person"></img>)}
            {Array.from({length: 6 - capacity - size}).map(() => <img className="icon-person-outline empty" src={personOutline} alt="person"></img>)}
        </div>
        <div className="lobby-buttons"></div>
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
        <div className="lobbies-page">
            <header>Lobbies of {userName}</header>
            <div className="lobbies">
                <div id="lobby-list">
                    {lobbies.lobbies.map((lobby) => (
                        <Lobby key={lobby.id} {...lobby} user={userName} />
                    ))}
                </div>
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

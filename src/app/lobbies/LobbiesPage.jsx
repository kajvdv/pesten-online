import { useContext, useState, useEffect, createContext, useRef } from "react";
import "./LobbiesPage.css";
import server, { getUser } from "../server";
import personOutline from "../../../public/9035563_person_outline_icon.svg";
import personFill from "../../../public/309035_user_account_human_person_icon.svg";


const LobbiesContext = createContext();


const VALUES = [
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "jack",
    "queen",
    "king",
    "ace",
]


function RuleMapping({index, selected, cardValue, onSelect, onDelete}) {
    const [currentValue, setCurrentValue] = useState(cardValue)

    return (
        <div className="rule-mapping">
            <select 
                onChange={e => {
                    onSelect(index, e.target.value)
                    setCurrentValue(e.target.value)
                }}
                defaultValue={currentValue}
            >
                {VALUES.map(value => currentValue == value || !selected.includes(value) ? <option value={value}>{value.charAt(0).toUpperCase() + value.slice(1)}</option> : null)}
            </select>
            <select name={currentValue}>
                {/* TODO: Change values to ints */}
                {/* TODO: Dynamically get rules from server */}
                <option value="Nog een keer">Nog een keer</option>
                <option value="Kaart pakken">Kaart pakken</option>
                <option value="Suit uitkiezen">Suit uitkiezen</option>
                <option value="Volgende speler beurt overslaan">Volgende speler beurt overslaan</option>
            </select>
            <button onClick={() => onDelete(index)} type="button">Delete</button>
        </div>
    )
}


function RuleMappings({}) {
    const [ruleCount, setRuleCount] = useState(0)
    const [selected, setSelected] = useState([])

    function deleteHandler(id) {
        console.log(id)
        setSelected(selected => selected.filter((_, i) => i != id))
    }

    function selectHandler(id, value) {
        setSelected(selected => selected.map((item, index) => id == index ? value : item))
    }

    function addHandler() {
        const difference = VALUES.filter(val => !selected.includes(val))
        if (!difference.length) return
        const value = difference[0]
        setSelected(selected => [...selected, value])
    }
    
    // Only one rule for each card
    const mappings = selected.map((cardValue, i) => <RuleMapping selected={[...selected]} onSelect={selectHandler} onDelete={deleteHandler} index={i} cardValue={cardValue} key={cardValue}/>)
    return (
        <div className="rule-mappings">
            {mappings}
            <button className="create-form-button" type="button" onClick={addHandler}>Add New Rule</button>
        </div>
    )
}


function Slider({name, min, max, onSelect}) {
    const [count, setCount] = useState(min)
    const [hoover, setHoover] = useState(min)

    useEffect(() => {
        // Resetting the count if it falls out of the range
        setCount(count => min <= count && count <= max ? count : min)
        setHoover(count => min <= count && count <= max ? count : min)
    }, [min, max])

    return (
        <div className="playericons" onMouseLeave={_ => setHoover(count)}>
            <input
                // readOnly={true}
                onChange={event => setCount(event.target.value)}
                style={{display: 'none'}}
                value={count}
                name={name}
                type="range"
                min={min}
                max={max}
            />    
            {Array.from({length: hoover}).map((_, index) => <img
                className="icon-person-fill"
                src={personFill}
                onMouseOver={event => setHoover(index+1 > min ? index+1 : min)}
                onClick={ _ => {
                    const value = index+1 > min ? index+1 : min
                    setCount(value)
                    if (onSelect) onSelect(value)
                }}
                alt="person"
            />)}
            {Array.from({length: max - hoover}).map((_, index) => <img
                className="icon-person-outline"
                src={personOutline}
                onMouseOver={event => setHoover(index+hoover+1)}
                alt="person"
            />)}
        </div>
    )
}


function CreateLobbyModal({ visible, onCancel, userName }) {
    const lobbies = useContext(LobbiesContext);
    const modalRef = useRef(null);
    const [error, setError] = useState(null)
    const [playerCount, setPlayerCount] = useState(2)

    function _onCancel() {
        setTimeout(() => {
            setError(null)
            modalRef.current.reset()
            setPlayerCount(2)
        }, 300) // For the animation
        onCancel()
    }

    useEffect(() => {
        console.log(playerCount)
    }, [playerCount])

    const formElements = (
        <>
            <label htmlFor="name">Name of game</label>
            <input name="name" type="text" defaultValue={userName + "'s game"}></input>
            <label htmlFor="size">Amount of players</label>
            <Slider name="size" min={2} max={6} onSelect={setPlayerCount}/>
            <label htmlFor="aiCount">Amount of AI's</label>
            {/* <input name="aiCount" type="number" min="0" max="5" defaultValue={0}></input> */}
            <Slider name="aiCount" min={0} max={playerCount-1}/>
            <h3>Special Rules</h3>
            <RuleMappings/>
            {error ? <p className="error-message">{error.response.data.detail}</p> : null}
            <div className="modal-buttons">
                <button className="create-form-button" type="button" onClick={_onCancel}>Cancel</button>
                <button className="create-form-button" type="submit">Create</button>
            </div>
        </>
    )

    return (<>
        <div className={"modal-overlay" + (visible ? " visible" : "")}></div>
        <div className={"create-modal" + (visible ? " visible" : "")}>
            <h1>Create a new game</h1>
            <form className="create-form" ref={modalRef} 
                onSubmit={async (event) => {
                    try {
                        event.preventDefault();
                        await lobbies.createLobby(new FormData(event.target));
                        _onCancel();
                    }
                    catch(err) {
                        setError(err)
                    }}}
            >
                {userName ? formElements : null}
            </form>
        </div>
    </>);
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
    const [showModal, setShowModal] = useState(true);

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

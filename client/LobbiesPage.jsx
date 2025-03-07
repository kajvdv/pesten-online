import { useContext, useState, useEffect, createContext, useRef, createElement } from "react";
// import "./LobbiesPage.css";
import server, { getUser } from "./server";
import PersonOutline from "./icons/human_outline.svg?react";
import PersonFill from "./icons/human_fill.svg?react";
import JokerOutline from "./icons/joker_outline.svg?react";
import JokerFill from "./icons/joker_fill.svg?react";
import { useNavigate } from "react-router-dom";


const LobbiesContext = createContext();


function RuleMapping({values, defaultValue, onSelect, onDelete}) {
    const [currentValue, setCurrentValue] = useState(defaultValue)
    const [currentRule, setCurrentRule] = useState("")
    const [drawCardCount, setDrawCardCount] = useState("2")

    return (
        <div className="rule-mapping">
            <select 
                onChange={e => {
                    onSelect(e.target.value)
                    setCurrentValue(e.target.value)
                }}
                defaultValue={currentValue}
            >
                {values.map(value => <option key={value} value={value}>{value.charAt(0).toUpperCase() + value.slice(1)}</option>)}
            </select>
            <select onChange={value => setCurrentRule(value.target.value)} name={currentValue}>
                {/* TODO: Change values to ints */}
                {/* TODO: Dynamically get rules from server */}
                <option value="another_turn">Nog een keer</option>
                <option value={"draw_card" + "-" + drawCardCount}>Kaart pakken</option>
                <option value="change_suit">Suit uitkiezen</option>
                <option value="skip_turn">Volgende speler beurt overslaan</option>
                <option value="reverse_order">Volgorde omdraaien</option>
            </select>
            {"draw_card" == currentRule.split('-')[0] ? <input onChange={value => setDrawCardCount(value.target.value)} type="number" min={2} defaultValue={2} max={5}></input> : null}
            <button onClick={onDelete} type="button">Delete</button>
        </div>
    )
}


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
    "joker",
]

function RuleMappings({}) {
    const [selected, setSelected] = useState([])

    function deleteHandler(id) {
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
    const mappings = selected
        .sort((a, b) => VALUES.indexOf(a) - VALUES.indexOf(b))
        .map((cardValue, i) => <RuleMapping 
            values={VALUES.filter(value => cardValue == value || !selected.includes(value))}
            onSelect={value => selectHandler(i, value)}
            onDelete={_ => deleteHandler(i)}
            defaultValue={cardValue}
            key={cardValue}
        />)

    return (
        <div className="rule-mappings">
            {mappings}
            <button className="create-form-button" type="button" onClick={addHandler}>Add New Rule</button>
        </div>
    )
}


function Slider({name, min, max, onSelect, iconFill, iconOutline}) {
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
            {Array.from({length: hoover}).map((_, index) => createElement(iconFill,
                {
                    className: "icon-person-fill",
                    onMouseOver: event => setHoover(index+1 > min ? index+1 : min),
                    onClick: _ => {
                        const value = index+1 > min ? index+1 : min
                        setCount(prev => {
                            if (value == prev) {
                                setHoover(min)
                                return min
                            }
                            return value
                        })
                        if (onSelect) onSelect(value)
                    },
                    onMouseOut: _ => setHoover(count),
                alt: 'fill'
                }
            ))}
            {Array.from({length: max - hoover}).map((_, index) => createElement(iconOutline,
                {
                    className: "icon-person-outline",
                    onMouseOver: event => setHoover(index+hoover+1),
                    onMouseOut: _ => setHoover(count),
                    alt: 'outline',
                }
            ))}
        </div>
    )
}


function CreateLobbyModal({ visible, onCancel, userName }) {
    const lobbies = useContext(LobbiesContext);
    const modalRef = useRef(null);
    const [error, setError] = useState(null)
    const [playerCount, setPlayerCount] = useState(2)
    const [renderForm, setRenderForm] = useState(visible)

    function _onCancel() {
        setTimeout(() => {
            setRenderForm(false)
        }, 300) // For the animation
        onCancel()
    }

    useEffect(_ => {
        if (!renderForm) {
            setPlayerCount(2)
            setError(null)
            setRenderForm(true)
        }
    }, [renderForm])

    // Everything in here will be unmounted on canceling the modal
    const formElements = (
        <>
            <label htmlFor="name">Name of game</label>
            <input name="name" type="text" defaultValue={userName + "'s game"}></input>
            <label htmlFor="size">Amount of players</label>
            <Slider iconOutline={PersonOutline} iconFill={PersonFill} name="size" min={2} max={6} onSelect={setPlayerCount}/>
            <label htmlFor="aiCount">Amount of AI's</label>
            {/* <input name="aiCount" type="number" min="0" max="5" defaultValue={0}></input> */}
            <Slider iconOutline={PersonOutline} iconFill={PersonFill} name="aiCount" min={0} max={playerCount-1}/>
            <label htmlFor="jokerCount">Amount of Jokers</label>
            <Slider iconOutline={JokerOutline} iconFill={JokerFill} name="jokerCount" min={0} max={5}/>
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
                {userName && renderForm ? formElements : null}
            </form>
        </div>
    </>);
}

function LobbiesProvider({ children }) {
    const [lobbies, setLobbies] = useState([]);
    const navigate = useNavigate()

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
        getLobbies().catch(error => {
            if (error.response.status && error.response.status == 401) {
                navigate('/')
            }
        })
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
    const navigate = useNavigate()

    useEffect(() => {
        if (!deleting) return
        lobbies.deleteLobby(id)
            .then(() => setDeleting(false))
    }, [deleting])

    function join() {
        navigate("/game?lobby_id=" + id)
    }

    return <div className="lobby" style={players.includes(user) ? {backgroundColor: 'yellow'} : {}}>
        <h1 className="lobby-join">{id}</h1>
        <div className="player-icons">
            {Array.from({length: size}).map(() => <PersonFill className="icon-person-fill" alt="person"/>)}
            {Array.from({length: capacity - size}).map(() => <PersonOutline className="icon-person-outline" alt="person"/>)}
            {Array.from({length: 6 - capacity - size}).map(() => <PersonOutline className="icon-person-outline empty" alt="person"/>)}
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

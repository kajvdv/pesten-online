import { useState } from "react"


function createLobby(event) {
    fetch('/lobbies', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: '{"size":2}'
    }).then(() => location.reload())
}

function Lobbies() {
    return <>
        <header>Lobbies</header>
        <div className="lobbies">
            <div id="lobby-list">
            </div>
            <button id="new-lobby-button" onclick={createLobby}>Create new</button>
        </div>
    </>
}

export default Lobbies
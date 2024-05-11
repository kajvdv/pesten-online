const queryString = window.location.search
const urlParams = new URLSearchParams(queryString);
const userName = urlParams.get('name')


function onCreateLobby(event) {
    fetch('/lobbies', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: '{"size":2}'
    }).then(() => location.reload())
}

const token = sessionStorage.getItem('access_token')
if (!token) {
    throw new Error("No token found in storage")
}
fetch('/lobbies', {headers: {'Authorization': "Bearer " + token}}).then(response => response.json()).then(data => {
    console.log(data)
    const lobbies = document.querySelector('.lobbies')
    for (let i = 0; i < data.length; i++) {
        const element = document.createElement('a')
        element.className = 'lobby'
        element.textContent = "Join game"
        element.href = `../board/index.html?name=${userName}&lobby_id=${i}`
        lobbies.prepend(element)
    }
})
import axios from "axios";

const server = axios.create({
    baseURL: 'http://localhost:8000',
})


async function getLobbies() {
    return server.get('/lobbies')
}

async function postLobby(size) {
    return server.post('/lobbies', {size})
}


getLobbies()
    .then(response => {
        console.log(response.data)
    })
    .then(() => postLobby(2))
    .then(response => {
        console.log(response.data)
    })


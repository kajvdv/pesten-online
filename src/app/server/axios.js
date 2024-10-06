import axios from "axios";

const accessToken = sessionStorage.getItem("accessToken")

const server = axios.create({
    baseURL: '/api',
    headers: accessToken ? {'Authorization': "BEARER " + accessToken} : {},
})


class GameConnection {
    constructor(lobby_id) {
        this.websocket = new WebSocket(
            `ws://${window.location.host}/api/lobbies/connect?lobby_id=${lobby_id}&token=${accessToken}`,
            
        )
    }

    onReceive(messageHandler, errorHandler) {
        this.websocket.addEventListener('message', event => {
            const data = JSON.parse(event.data)
            console.log(data)
            if ('error' in data) {
                errorHandler(data.error)
                console.log(data.error)
            } else {
                messageHandler(data)
            }
        })
    }

    send(index) {
        this.websocket.send(index)
    }
}


async function login(form) {
    const response = await server.post("/token", form)
    const {token_type, access_token} = response.data
    const headerField = token_type.toUpperCase() + " " + access_token
    server.defaults.headers.common['Authorization'] = headerField
    sessionStorage.setItem('accessToken', access_token)
}


async function connect(lobbyId) {
    const connection = new GameConnection(lobbyId)
    return connection
}


async function getUser() {
    const token = sessionStorage.getItem('accessToken')
    if (!token) {
        throw new Error("No token in client storage")
    }
    const user = atob(token.split('.')[1])
    return JSON.parse(user).sub
}


async function getLobbies() {
    const response = await server.get('/lobbies')
    return response.data
}

async function postLobby(size) {
    const response = await server.post('/lobbies', {size})
    return response.data
}

async function deleteLobby(id) {
    const response = await server.delete(`/lobbies/${id}`)
    return response.data
}


export default {
    login,
    connect,
    getUser,
    getLobbies,
    postLobby,
    deleteLobby,
}

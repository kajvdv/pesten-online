import axios from "axios";


const accessToken = ""

const server = axios.create({
    baseURL: '/api',
    headers: Boolean(accessToken) ? {'Authorization': "BEARER " + accessToken} : {},
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
            if ('error' in data) {
                errorHandler(data.error)
            } else {
                errorHandler("")
                messageHandler(data)
            }
        })
        this.websocket.addEventListener("close", event => {
            errorHandler("Lost connection with the server")
            console.log('close', event)
        })
        this.websocket.addEventListener('open', event => {
            console.log("Opening websocket")
        })
    }

    close() {
        this.websocket.close()
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


export async function connect(lobbyId) {
    const connection = new GameConnection(lobbyId)
    return connection
}


export async function getUser() {
    const token = sessionStorage.getItem('accessToken')
    if (!token) {
        throw new Error("No token in client storage")
    }
    const user = atob(token.split('.')[1])
    return JSON.parse(user).sub
}


export default server

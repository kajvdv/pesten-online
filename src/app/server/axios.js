import axios from "axios";

const accessToken = sessionStorage.getItem("accessToken")

const server = axios.create({
    baseURL: '/api',
    headers: accessToken ? {'Authorization': "BEARER " + accessToken} : {},
})


async function login(form) {
    const response = await server.post("/token", form)
    const {token_type, access_token} = response.data
    const headerField = token_type.toUpperCase() + " " + access_token
    server.defaults.headers.common['Authorization'] = headerField
    sessionStorage.setItem('accessToken', access_token)
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
    getUser,
    getLobbies,
    postLobby,
    deleteLobby,
}

import axios from "axios";

const accessToken = sessionStorage.getItem("accessToken")

const server = axios.create({
    baseURL: '/api',
    headers: accessToken ? {'Authorization': accessToken} : {},
})


async function login(form) {
    const response = await server.post("/token", form)
    const {token_type, access_token} = response.data
    const headerField = token_type.toUpperCase() + " " + access_token
    server.defaults.headers.common['Authorization'] = headerField
    sessionStorage.setItem('accessToken', headerField)
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
    getLobbies,
    postLobby,
    deleteLobby,
}

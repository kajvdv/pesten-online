import lobbies from './dummy_data/lobbies.json'


export default {
    login: async () => lobbies,
    getLobbies: async () => lobbies,
    postLobby: async () => lobbies,
    deleteLobby: async () => {
        await new Promise(r => setTimeout(r, 1000))
        return lobbies
    },
}
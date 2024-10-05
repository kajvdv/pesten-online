import lobbies from './dummy_data/lobbies.json'

const lobbiesWithRightIds = lobbies.map((lobby, index) => ({...lobby, id: index}))


export default {
    login: async () => lobbiesWithRightIds,
    getLobbies: async () => lobbiesWithRightIds,
    postLobby: async () => lobbiesWithRightIds,
    getUser: async () => "dummyUser",
    deleteLobby: async () => {
        await new Promise(r => setTimeout(r, 1000))
        return lobbiesWithRightIds
    },
}
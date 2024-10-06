import lobbies from './dummy_data/lobbies.json'
import board from './dummy_data/board.json'

const lobbiesWithRightIds = lobbies.map((lobby, index) => ({...lobby, id: index}))

class DummyConnection {
    constructor(lobbyId) {

    }

    onReceive(messageHandler, errorHandler) {
        console.log("Dummy board", board)
        messageHandler(board)
    }

    onSend(index) {
        console.log("Dummy connection reveived index of", index)
    }
}

export default {
    login: async () => lobbiesWithRightIds,
    connect: async () => new DummyConnection(),
    getLobbies: async () => lobbiesWithRightIds,
    postLobby: async () => lobbiesWithRightIds,
    getUser: async () => "dummyUser",
    deleteLobby: async () => {
        await new Promise(r => setTimeout(r, 1000))
        return lobbiesWithRightIds
    },
}
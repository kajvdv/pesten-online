import {getLobbies, postLobby, deleteLobby, login} from './server.js'


const form = new FormData()
form.append("username", 'admin')
form.append("password", 'admin')
login(form)
    .then(() => getLobbies())
    .then(response => {
        console.log(response.data)
    })
    .catch(error => {
        console.log(error)
    })

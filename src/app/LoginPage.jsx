import { useRef, useState, useContext} from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Login.css'
import server from './server'

function LoginPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const loginForm = useRef()
    // const navigate = useNavigate()

    async function submit(event) {
        event.preventDefault()
        const response = await server.post("/token", loginForm.current)
        const {token_type, access_token} = response.data
        const headerField = token_type.toUpperCase() + " " + access_token
        server.defaults.headers.common['Authorization'] = headerField
        sessionStorage.setItem('accessToken', access_token)
        
        // navigate('/lobbies')
        window.location.href = '/lobbies'
    }

    return (
        <form ref={loginForm} id="login-form" onSubmit={submit}>
            <input id="username" name="username" type="text" placeholder="Username" onChange={val => setUsername(val.target.value)} value={username} size="25" required  />
            <input id="password" name="password" type="password" placeholder="Password" onChange={val => setPassword(val.target.value)} value={password} size="25" required  />
            <input type="submit" value="Login" />
            <Link to='register' className="register-link">Register</Link>
        </form>
    )
}

export default LoginPage
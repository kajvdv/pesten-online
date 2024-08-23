import { useRef, useState, useContext} from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from './AuthProvider'
import './Login.css'

function LoginPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const loginForm = useRef()
    const navigate = useNavigate()
    const [accessToken, setAccessToken] = useContext(AuthContext)

    async function submit(event) {
        event.preventDefault()
        const form = new FormData(loginForm.current)
        const response = await fetch('/api/token', {method: 'post', body: form})
        if (!response.ok) {
            return
        }
        const { access_token, token_type } = await response.json()
        setAccessToken(token_type.toUpperCase() + " " + access_token)
        navigate('/lobbies')
    }

    return (
        <form ref={loginForm} id="login-form" onSubmit={submit}>
            <input id="username" name="username" type="text" placeholder="Username" onChange={val => setUsername(val.target.value)} value={username} size="25" required  />
            <input id="password" name="password" type="password" placeholder="Password" onChange={val => setPassword(val.target.value)} value={password} size="25" required  />
            <input type="submit" value="Login" />
            <a className="register-link" href="register">Register</a>
        </form>
    )
}

export default LoginPage
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
// import './Login.css'

function RegisterPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const registerForm = useRef()
    const navigate = useNavigate()

    async function submit(event) {
        event.preventDefault()
        const form = new FormData(registerForm.current)
        const response = await fetch('/api/register', {method: 'post', body: form})
        if (response.status != '204') {
            throw new Error("Failed to register", registerForm.username)
        }
        navigate('/')
    }

    return (
        <form ref={registerForm} id="register-form" onSubmit={submit}>
            <input id="username" name="username" type="text" placeholder="Username" onChange={val => setUsername(val.target.value)} value={username} size="25" required  />
            <input id="password" name="password" type="password" placeholder="Password" onChange={val => setPassword(val.target.value)} value={password} size="25" required  />
            <input type="submit" value="Register" />
        </form>
    )
}

export default RegisterPage
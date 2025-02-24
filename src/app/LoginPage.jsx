import { useRef, useState, useContext} from 'react'
import { Link, useNavigate } from 'react-router-dom'
// import './Login.css'
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
        <div className='login-page'>
            <title>Pesten</title>
            <form ref={loginForm} className="login-form" onSubmit={submit}>
                <input id="username" name="username" type="text" placeholder="Username" onChange={val => setUsername(val.target.value)} value={username} size="25" required  />
                <input id="password" name="password" type="password" placeholder="Password" onChange={val => setPassword(val.target.value)} value={password} size="25" required  />
                <button className='form-button'>Register</button>
                <input className='form-button' type="submit" value="Login" />
                {/* <Link to='register' className="register-link">Register</Link> */}
            </form>
            <img className='falling-card card-animation1' src='game\cards\3_of_hearts.png'></img>
            <img className='falling-card card-animation2' src='game\cards\4_of_hearts.png'></img>
            <img className='falling-card card-animation3' src='game\cards\5_of_clubs.png'></img>
            <img className='falling-card card-animation4' src='game\cards\6_of_spades.png'></img>
            <img className='falling-card card-animation5' src='game\cards\7_of_hearts.png'></img>
        </div>
    )
}

export default LoginPage
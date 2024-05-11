
const loginForm = document.getElementById('login-form')
loginForm.addEventListener('submit', async event => {
    event.preventDefault()
    const form = new FormData(loginForm)
    const { access_token, token_type } = await (await fetch('/token', {method: 'post', body: form})).json()
    const token = token_type + " " + access_token
    localStorage.setItem("access_token", token)
    window.location = "lobbies/index.html"
})

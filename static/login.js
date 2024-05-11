
const loginForm = document.getElementById('login-form')
loginForm.addEventListener('submit', async event => {
    event.preventDefault()
    const form = new FormData(loginForm)
    const response = await fetch('/token', {method: 'post', body: form})
    if (!response.ok) {
        return
    }
    const { access_token, token_type } = await response.json()
    const token = access_token
    sessionStorage.setItem("access_token", token)
    window.location.assign('lobbies/index.html')
})

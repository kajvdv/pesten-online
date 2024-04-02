


fetch('/lobbies').then(response => response.json()).then(data => {
    console.log(data)
    const lobbies = document.querySelector('.lobbies')
    for (let i = 0; i < data.length; i++) {
        const element = document.createElement('a')
        element.className = 'lobby'
        element.textContent = "Join game"
        element.href = `../board/index.html?name=kaj&lobby_id=${i}`
        lobbies.appendChild(element)
    }
})
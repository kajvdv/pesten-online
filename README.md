Install the project with `pip install -e .`
Initialize the database `python -m init_db`. It uses sqlite, so that should be installed.
Run the server with `python -m server` or `uvicorn server:app`

Run an html file in live server to develop on it. Live server acts as a proxy to prevent CORS errors.


## Creating a new game
Player can create a new empty lobby from the lobbies page. They do not own the lobby. It is possible that four other people than the creator can join.
Therefor, the creator will automatically join the created lobby.
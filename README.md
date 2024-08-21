Install the project with `pip install -e .`
Initialize the database `python -m pesten.init_db`. It uses sqlite, so that should be installed.
Run the server with `python -m server` or `uvicorn pesten.server:app`
Run the frontend dev server with `npm run dev`

Run an html file in live server to develop on it. Use the live server as a proxy to the backend.


## Creating a new game
Player can create a new empty lobby from the lobbies page. They do not own the lobby. It is possible that four other people than the creator can join.
Therefor, the creator will automatically join the created lobby.
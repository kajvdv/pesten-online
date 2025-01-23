Install the project with `pip install -e .`
Initialize the database `python -m pesten.init_db`. It uses sqlite, so that should be installed.
Run the server with `python -m pesten.server` or `uvicorn pesten.server:app`

Build the frontend with `npm run build`.
Run the frontend server with `npm run preview`.

Run `npm run dev` to run the frontend with dummy data

## Things
- better use of uvicorn. No more scripts per environment config. 
- Have win conditions
- Choose how many people can join
- comparing users with each other
- Selecting which rules to use
- Aangeven welke lobbies al zijn begonnen

## Dev environment things
- formatter installeren
- dummy data weghalen en calls misschien wel hardcoded in components
- Bestanden beter verdelen in kleinere testbare delen. Websocket server in apart project
- Database in apart project
- Hoe websocket authenticaten
- Betere logs hebben

## Testing

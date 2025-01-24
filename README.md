Install the project with `pip install -e .`
Initialize the database `python -m server.init_db`. It uses sqlite, so that should be installed.
Run the server with `uvicorn server.server:app`. Use the `--reload` flag to reload on save

Build the frontend with `npm run build`.
Run the frontend server with `npm run preview`.

Run `npm run dev` to run the frontend with dummy data

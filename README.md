Install the project with `pip install -e .`
Initialize the database `python -m pesten.init_db`. It uses sqlite, so that should be installed.
Run the server with `python -m pesten.server` or `uvicorn pesten.server:app`

Build the frontend with `npm run build`.
Run the frontend server with `npm run preview`.

Run the dev server with `python -m pesten.dev.server` to skip authentication

Run `npm run dev` to run the frontend with dummy data

## Testing

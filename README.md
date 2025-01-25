Install the project with `pip install -e .`
Initialize the database `python -m server.init_db`. It uses sqlite, so that should be installed.
Run the server with `uvicorn server.server:app --env-file=.env.local`. Use the `--reload` flag to reload on save
As you can see you'll need an env file containing a SECRET_KEY key, which contains the encryption key.
This key can be obtained by running `openssl rand -hex 32`. For windows you can use git bash to run this command.

Build the frontend with `npm run build`.
Run the frontend server with `npm run preview`.

Run `npm run dev` to run the frontend with dummy data

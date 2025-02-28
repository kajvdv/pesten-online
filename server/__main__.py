import sys

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv(".env.local")

import uvicorn
uvicorn.run("server.server:app", reload='--reload' in sys.argv)
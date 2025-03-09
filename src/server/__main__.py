import sys

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv(".env.local")

import logging

import uvicorn

logger = logging.basicConfig(level=logging.DEBUG)

uvicorn.run("server.server:app", reload='--reload' in sys.argv)
from fastapi import APIRouter
from pydantic import BaseModel


users = {}


def create_user(username, password):
    if username in users:
        raise Exception("User already exists")
    users[username] = password


def delete_user(username):
    if username in users:
        del users[username]
    else:
        raise Exception("User does not exists")

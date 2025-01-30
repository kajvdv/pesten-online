from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from server.server import app
from server.auth import get_current_user
from server.lobby import Lobbies, LobbyCreate



class PasswordRequestFormOverride:
    def __init__(self):
        self.username = "admin"
        self.password = "admin"


class LobbiesOverride(Lobbies):
    def __init__(self):
        ...

    def create_lobby(self, lobby_create: LobbyCreate, user):
        return {
            'id': lobby_create.name,
            'size': 1 + lobby_create.aiCount,
            'capacity': lobby_create.size,
            'creator': user,
            'players': [user],
        }


app.dependency_overrides[get_current_user] = lambda: "test"
app.dependency_overrides[OAuth2PasswordRequestForm] = PasswordRequestFormOverride
app.dependency_overrides[Lobbies] = LobbiesOverride


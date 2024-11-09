from sqlalchemy import select
import uvicorn

from pesten.server import app
from pesten.auth import get_current_user, User
from pesten.database import get_db
import pesten.lobby

pesten.lobby.lobbies = {0: pesten.lobby.Game(2, 'admin')}

def get_current_user_override(name: str = 'admin'):
    # stmt = select(User)
    # for db in get_db():
    #     row = db.execute(stmt).first()
    # return row.User
    user = User(username=name, password="test")
    print("logging in as", user.username)
    return user.username

app.dependency_overrides[get_current_user] = get_current_user_override

# if __name__ == "__main__":
#     uvicorn.run(["dev_server:app", '--reload'])
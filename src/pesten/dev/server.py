from sqlalchemy import select
import uvicorn

from pesten.server import app
from pesten.auth import get_current_user, User
from pesten.database import get_db

def get_current_user_override():
    stmt = select(User)
    for db in get_db():
        row = db.execute(stmt).first()
    return row.User

app.dependency_overrides[get_current_user] = get_current_user_override

if __name__ == "__main__":
    uvicorn.run(app)
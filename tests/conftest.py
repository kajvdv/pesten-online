import os
os.environ['ACCESS_TOKEN_SECRET'] = '27d63347d36d97b05669a6ca6c4e9372e78d1e897dcf5debe823db3bde12460d'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session
from httpx import AsyncClient

from server.auth import User, get_current_user
from server.server import app
from server.database import get_db, Base


engine = create_engine(
    "sqlite://",
    connect_args={
        'check_same_thread': False
    },
    poolclass=StaticPool
)

def get_db_override():
    with Session(engine) as db:
        yield db

def get_current_user_override(name_override: str = "test"):
    user = User(username=name_override, password='test')
    return user.username

@pytest.fixture
def db():
    for db in get_db_override():
        yield db


@pytest.fixture
async def async_client():
    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    test_client = AsyncClient(app=app)
    Base.metadata.create_all(engine)
    async with test_client:
        yield test_client
    Base.metadata.drop_all(engine)

@pytest.fixture
def client_with_auth(): # only used to test auth stuff
    app.dependency_overrides[get_db] = get_db_override
    test_client = TestClient(app)
    Base.metadata.create_all(engine)
    with test_client:
        yield test_client
    Base.metadata.drop_all(engine)
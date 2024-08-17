import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session

from auth import User, get_current_user
from server import app
from database import get_db, Base


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

def get_current_user_override():
    return User(username='test', password='test')


#TODO Option to not auth with testclient. Auth needed to test auth (duh)
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    test_client = TestClient(app)
    Base.metadata.create_all(engine)
    with test_client:
        yield test_client
    Base.metadata.drop_all(engine)

@pytest.fixture
def client_with_auth():
    app.dependency_overrides[get_db] = get_db_override
    test_client = TestClient(app)
    Base.metadata.create_all(engine)
    with test_client:
        yield test_client
    Base.metadata.drop_all(engine)
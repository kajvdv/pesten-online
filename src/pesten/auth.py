from subprocess import Popen
import requests
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import String, Integer, Column, insert, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pesten.database import Base, get_db

SECRET_KEY = "27d63347d36d97b05669a6ca6c4e9372e78d1e897dcf5debe823db3bde12460d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

class User(Base):
    __tablename__ = "user"

    username = Column(String, primary_key=True)
    password = Column(String)

    def __repr__(self) -> str:
        return f"username={self.username} password={self.password}"


def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(token = Depends(oath2_scheme)):
    user = decode_token(token)
    return user['sub']


invalid_response = HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
@router.post('/token')
def get_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    stmt = select(User).where(User.username == form.username)
    row = db.execute(stmt).first()
    if not row:
        raise invalid_response
    print(row.User)
    hashed_password = row.User.password
    if not pwd_context.verify(form.password, hashed_password):
        raise invalid_response
    token = jwt.encode(
        {"sub": form.username, 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post('/register', status_code=204)
def register_user(username = Form(), password = Form(), db: Session = Depends(get_db)):
    print("Creating user")
    # if username in users:
    #     return "User already exists"
    # users[username] = pwd_context.hash(password)
    hashed_password = pwd_context.hash(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        print("User already exists")
        db.rollback()


@router.get('/users/me')
def get_user(user = Depends(get_current_user)):
    print(user)
    return user
from subprocess import Popen
import requests
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = "27d63347d36d97b05669a6ca6c4e9372e78d1e897dcf5debe823db3bde12460d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

class User:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

users = {}


def get_current_user(token = Depends(oath2_scheme)):
    user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return user['sub']


@router.post('/token')
def get_token(form: OAuth2PasswordRequestForm = Depends()):
    invalid_response = HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if form.username not in users:
        raise invalid_response
    hashed_password = users[form.username]
    if not pwd_context.verify(form.password, hashed_password):
        raise invalid_response
    token = jwt.encode(
        {"sub": form.username, 'exp': datetime.now(timezone.utc) + timedelta(minutes=15)},
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post('/register')
def register_user(username = Form(), password = Form()):
    print("Creating user")
    if username in users:
        return "User already exists"
    users[username] = pwd_context.hash(password)


@router.get('/users/me')
def get_user(user = Depends(get_current_user)):
    print(user)
    return user


if __name__ == "__main__":
    # Start server with 'uvicorn auth_new:app'
    token_response = requests.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
    print("Inloggen met onbekende user:", token_response.text)
    register_response = requests.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
    print("User registreren:", register_response.text)
    register_response = requests.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
    print("User registreren met bestaande user:", register_response.text)
    token_response = requests.post("http://localhost:8000/token", data={'username': "kaj", 'password': '124'})
    print("Inloggen met verkeerde wachtwoord:", token_response.text)
    token_response = requests.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
    print("Inloggen met goed wachtwoord:", token_response.json())
    access_token = token_response.json()
    user_response = requests.get("http://localhost:8000/users/me", headers={"Authorization": "Bearer" + " " + access_token['access_token']})
    print("Data krijgen van user", user_response.text)

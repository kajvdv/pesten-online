#TODO: Implement hashing
#TODO: Replace prints with logger statements
#TODO: Return a JWT token instead of just the username
from fastapi import Depends, Form, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from user import create_user, delete_user
import user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme)):
    return user.users[token]


def hash_password():
    ...


def get_user_from_token(token):
    if token in user.users:
        return token
    else:
        raise Exception("User does not exists")


@router.post('/token')
def login_user(form: OAuth2PasswordRequestForm = Depends()):
    if form.username not in user.users:
        print("Could not find user:", form.username)
        print(user.users)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )

    if user.users[form.username] != form.password:
        print("Wrong password for", form.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
    print("Succesful login for", form.username)
    return {"access_token": form.username, "token_type": "bearer"}


@router.post('/register')
def register_user(username = Form(), password = Form()):
    print("Registerd", username, password)
    create_user(username, password)
    # I don't like it that it is refering to a hardcoded html file. Should not know about it.
    return RedirectResponse('static/home.html', status.HTTP_303_SEE_OTHER)


# if __name__ == "__main__":
#     from fastapi import FastAPI
#     import user
#     from fastapi.testclient import TestClient
#     app = FastAPI()
#     app.include_router(router)
#     client = TestClient(app)
#     client.post("register", data={'username': 'kaj', 'password': '1234'})
#     print('users:', user.users)
#     response = client.post('token', data={'username': 'kaj', 'password': '123'})
#     print(response.status_code, response.read())
#     response = client.post('token', data={'username': 'kaj', 'password': '1234'})
#     print(response.status_code, response.read())


    

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)
    
token_response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
print("Inloggen met onbekende user:", token_response.text)
register_response = client.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
print("User registreren:", register_response.text)
register_response = client.post("http://localhost:8000/register", data={'username': "kaj", 'password': '123'})
print("User registreren met bestaande user:", register_response.text)
token_response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': '124'})
print("Inloggen met verkeerde wachtwoord:", token_response.text)
token_response = client.post("http://localhost:8000/token", data={'username': "kaj", 'password': '123'})
print("Inloggen met goed wachtwoord:", token_response.json())
access_token = token_response.json()
user_response = client.get("http://localhost:8000/users/me", headers={"Authorization": "Bearer" + " " + access_token['access_token']})
print("Data krijgen van user", user_response.text)

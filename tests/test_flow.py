import subprocess
import time

import pytest
import requests
from websockets.sync.client import connect

from pesten.server import app
from conftest import get_current_user_override, get_db, get_current_user, get_db_override


app.dependency_overrides[get_db] = get_db_override
app.dependency_overrides[get_current_user] = get_current_user_override
new_app = app

def test_game_flow():
    server_process = subprocess.Popen(['uvicorn', 'test_flow:new_app', '--http h11'], shell=False, stdout=subprocess.DEVNULL)
    
    try:
        time.sleep(1)
        response = requests.post('http://localhost:8000/lobbies?name_override=kaj', json={'size': 2})
        print(response.text)
        with (
            connect(f'ws://localhost:8000/lobbies/connect?name_override=kaj&lobby_id={response.text}') as connection_kaj,
            connect(f'ws://localhost:8000/lobbies/connect?name_override=soy&lobby_id={response.text}') as connection_soy,
        ):
            message = connection_soy.recv()
            message = connection_kaj.recv()
            # print(message)
            connection_kaj.send('-1')
            message = connection_soy.recv()
            message = connection_kaj.recv()
            # print(message)
            connection_soy.send('-1')
            message = connection_soy.recv()
            message = connection_kaj.recv()
            print("Did all the turns")
    finally:
        print("Terminate server process")
        server_process.terminate()
    
if __name__ == "__main__":
    # test_game_flow()
    pytest.main([__file__])
import subprocess
import time
import requests
from websockets.sync.client import connect


if __name__ == "__main__":
    server_process = subprocess.Popen(['uvicorn', 'server:app'])
    try:
        time.sleep(1)
        response = requests.post('http://localhost:8000/lobbies', json={'size': 2})
        print(response.text)
        with (
            connect(f'ws://localhost:8000/pesten?name=kaj&lobby_id={response.text}') as connection_kaj,
            connect(f'ws://localhost:8000/pesten?name=soy&lobby_id={response.text}') as connection_soy,
        ):
            for _ in range(3):
                message = connection_kaj.recv()
                message = connection_soy.recv()
                print(message)
                connection_kaj.send('-1')
                message = connection_soy.recv()
                message = connection_kaj.recv()
                print(message)
                connection_soy.send('-1')
            message = connection_soy.recv()
            message = connection_kaj.recv()
            print("Did all the turns")
    finally:
        print("Terminate server process")
        server_process.terminate()
    
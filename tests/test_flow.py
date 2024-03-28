import subprocess
import time
from websockets.sync.client import connect


if __name__ == "__main__":
    server_process = subprocess.Popen(['uvicorn', 'server:app'])
    time.sleep(3)
    with (
        connect('ws://localhost:8000/?name=kaj') as connection_kaj,
        connect('ws://localhost:8000/?name=soy') as connection_soy,
    ):
        for _ in range(10):
            message = connection_kaj.recv()
            print(message)
            connection_kaj.send('-1')
            message = connection_soy.recv()
            print(message)
            connection_soy.send('-1')
    print("Terminate server process")
    server_process.terminate()
    
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
        message = connection_kaj.recv()
        print(message)
    print("Terminate server process")
    server_process.terminate()
    
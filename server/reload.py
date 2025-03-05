from pathlib import Path
import os
import pickle

from server.lobby.lobby import AIConnection
from server.lobby.dependencies import Lobbies


lobbies_dir = Path.cwd() / os.environ.get('LOBBIES_DIR', 'data/lobbies')

def save_lobbies(lobbies):
    lobbies_dir.mkdir(parents=True, exist_ok=True)
    print("made", lobbies_dir)
    print(lobbies)
    for name, lobby in lobbies.items():
        path = lobbies_dir / f'{name}.pickle'
        print(path)
        game = lobby.game
        creator = lobby.creator
        chooses = lobby.chooses
        ai_count = len([player.connection for player in lobby.players if type(player.connection) == AIConnection])
        print(lobby.players)
        with open(path, 'wb') as file:
            pickle.dump([game, creator, chooses, ai_count], file)

async def load_lobbies(lobbies):
    for lobby_path in lobbies_dir.iterdir():
        with open(lobby_path, 'rb') as file:
            game, creator, chooses, ai_count = pickle.load(file)
            lobbies_crud = Lobbies(creator, lobbies)
            await lobbies_crud.create_lobby(lobby_path.stem, ai_count, game)
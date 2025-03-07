from pathlib import Path
import os
import pickle

from server.lobby.lobby import AIConnection
from server.lobby.dependencies import Lobbies, Player, NullConnection
from server.lobby.routes import create_lobby_route


lobbies_dir = Path.cwd() / os.environ.get('LOBBIES_DIR', 'data/lobbies')

def save_lobbies(lobbies, lobbies_create_parameters):
    lobbies_dir.mkdir(parents=True, exist_ok=True)
    for file in lobbies_dir.iterdir():
        file.unlink()
    for name, lobby in lobbies.items():
        path = lobbies_dir / f'{name}.pickle'
        game = lobby.game
        creator = lobby.creator
        chooses = lobby.chooses
        player_names = [p.name for p in lobby.players]
        lobby_create = lobbies_create_parameters[name]
        ai_count = len([player.connection for player in lobby.players if type(player.connection) == AIConnection])
        with open(path, 'wb') as file:
            pickle.dump([game, creator, player_names, chooses, ai_count, lobby_create], file)

async def load_lobbies(lobbies, lobbies_create_parameters):
    for lobby_path in lobbies_dir.iterdir():
        with open(lobby_path, 'rb') as file:
            game, creator, player_names, chooses, ai_count, lobby_create = pickle.load(file)
        lobbies_crud = Lobbies(creator, lobbies)
        # await lobbies_crud.create_lobby(lobby_path.stem, ai_count, game)
        await create_lobby_route(
            lobby_create,
            lobbies_crud,
            game,
            creator,
            lobbies_create_parameters,
        )
        lobby = lobbies[lobby_create.name]
        lobby.chooses = chooses
        for name in player_names:
            # This might seem that these NullConnections will override the AIConnections established in create_lobby_route.
            # However, the connect function of the AIConnection created in create_lobby_route will execute AFTER this coroutine is finished.
            # These AIConnections will then override these NullConnections and thus putting things back to normal
            await lobby.connect(Player(name, NullConnection()))

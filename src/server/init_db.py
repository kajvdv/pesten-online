from server.database import Base, engine, get_db
from server.auth import register_user
import server.server # Make sure all the orm models are imported

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

for db in get_db():
    register_user('admin', 'admin', db)

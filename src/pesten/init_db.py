from database import Base, engine, get_db
from auth import register_user
import pesten.server # Make sure all the orm models are imported

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

for db in get_db(): # This is like with-statement
    register_user('admin', 'admin', db)

from database import Base, engine
import server # Make sure all the orm models are imported

Base.metadata.create_all(engine)
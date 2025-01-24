from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, DeclarativeBase

engine = create_engine('sqlite:///data.db')

class Base(DeclarativeBase):
    ...

def get_db():
    with Session(engine) as db:
        yield db

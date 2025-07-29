from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated

DATABASE_URL = "sqlite:///shoppinglist.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]

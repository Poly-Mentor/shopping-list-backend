from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated

DATABASE_URL = "sqlite:///shoppinglist.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

# Allow overriding the engine for testing
_test_engine = None

def set_test_engine(test_engine):
    """Set a test engine to be used instead of the default engine."""
    global _test_engine
    _test_engine = test_engine
    # Create tables for the test engine if it's not None
    if test_engine is not None:
        SQLModel.metadata.create_all(test_engine)

def initialize_test_database():
    """Initialize the test database by creating all tables."""
    if _test_engine is not None:
        SQLModel.metadata.create_all(_test_engine)

def get_engine():
    """Get the current engine (test engine if set, otherwise default engine)."""
    global _test_engine
    if _test_engine is not None:
        return _test_engine
    return engine

def create_db_and_tables():
    # Always create tables, even in testing
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(get_engine()) as session:
        yield session

DBSessionDep = Annotated[Session, Depends(get_session)]

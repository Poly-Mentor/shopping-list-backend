import pytest
import os
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.models import User, ShoppingList, UserListPermission
from app.data import db

# Set the TESTING environment variable
os.environ["TESTING"] = "1"

# Create an in-memory SQLite database for testing
@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    # Use an in-memory SQLite database for testing
    # Add check_same_thread=False to allow usage across threads
    engine = create_engine("sqlite:///:memory:", echo=True, connect_args={"check_same_thread": False})
    # Create all tables for the test engine
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture(name="session", scope="function")
def session_fixture(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(name="client", scope="function")
def client_fixture(engine, session):
    # Create a fresh app instance for each test to ensure it uses the test engine
    from fastapi import FastAPI
    from contextlib import asynccontextmanager
    from app.routers import user, shoppinglist, userlistpermission
    from app.data import db

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Create tables for the test engine
        SQLModel.metadata.create_all(engine)
        yield
        # Cleanup actions can be added here if needed

    app = FastAPI(lifespan=lifespan)
    app.include_router(user.router)
    app.include_router(shoppinglist.router)
    app.include_router(userlistpermission.router)

    # Override the get_session dependency with our test session
    def get_session_override():
        yield session

    # Override only the get_session dependency
    app.dependency_overrides[db.get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="sample_user")
def sample_user_fixture(session):
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    # Ensure the id is not None after commit
    assert user.id is not None
    return user

@pytest.fixture(name="sample_list")
def sample_list_fixture(session, sample_user):
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    # Ensure the id is not None after commit
    assert shopping_list.id is not None
    
    # Create a permission linking the user to the list
    # Ensure the ids are not None
    assert sample_user.id is not None
    permission = UserListPermission(user_id=sample_user.id, list_id=shopping_list.id)
    session.add(permission)
    session.commit()
    
    return shopping_list

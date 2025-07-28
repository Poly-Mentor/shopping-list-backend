import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.main import app
from app.data.db import get_session
from app.models import User, ShoppingList, UserListPermission, ShoppingItem

# Create an in-memory SQLite database for testing
@pytest.fixture(name="engine")
def engine_fixture():
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(engine):
    # Override the get_session dependency with our test session
    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
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

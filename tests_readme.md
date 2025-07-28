# Testing Guide for FastAPI + SQLModel Applications

This document explains the proper approach to testing FastAPI applications with SQLModel, based on the issues encountered and solutions implemented in this project.

## Table of Contents
1. [Overview](#overview)
2. [Test Architecture](#test-architecture)
3. [Common Pitfalls](#common-pitfalls)
4. [Best Practices](#best-practices)
5. [Test Structure](#test-structure)
6. [Troubleshooting](#troubleshooting)

## Overview

Testing FastAPI applications with SQLModel requires careful consideration of database session management, dependency injection, and test isolation. The main challenge is ensuring that test data is properly shared between direct database operations and HTTP requests made through the FastAPI test client.

## Test Architecture

### Key Components

1. **Test Database Engine**: In-memory SQLite database for each test
2. **Session Management**: Shared session between test fixtures and FastAPI app
3. **Dependency Overrides**: Replace production dependencies with test versions
4. **Test Client**: FastAPI TestClient configured with test dependencies

### File Structure
```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_main.py            # Main app endpoint tests
├── test_models.py          # Database model tests
├── test_*_service.py       # Service layer tests (direct function calls)
├── test_*_router.py        # Router tests (HTTP requests via TestClient)
└── tests_readme.md         # This documentation
```

## Common Pitfalls

### 1. ❌ Creating Module-Level TestClient

**Wrong:**
```python
# test_user_router.py
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)  # ❌ Uses production app

def test_get_users(client: TestClient, session: Session):
    # This creates a conflict - module client vs fixture client
    response = client.get("/user/")
```

**Correct:**
```python
# test_user_router.py
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_get_users(client: TestClient, session: Session):  # ✅ Use fixture client
    response = client.get("/user/")
```

### 2. ❌ Session Isolation Issues

**Wrong:**
```python
@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:  # ❌ Different session per fixture
        yield session

@pytest.fixture(name="client")
def client_fixture(engine):
    def get_session_override():
        with Session(engine) as session:  # ❌ Another different session
            yield session
```

**Correct:**
```python
@pytest.fixture(name="session")
def session_fixture(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)  # ✅ Shared connection
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(name="client")
def client_fixture(engine, session):  # ✅ Use the same session
    def get_session_override():
        yield session  # ✅ Same session instance
```

### 3. ❌ Improper Database Setup

**Wrong:**
```python
# Not setting test engine properly
def test_something():
    # Test runs against production database
```

**Correct:**
```python
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:", echo=True, 
                          connect_args={"check_same_thread": False})
    set_test_engine(engine)  # ✅ Configure app to use test engine
    SQLModel.metadata.create_all(engine)
    yield engine
    set_test_engine(None)  # ✅ Clean up
```

## Best Practices

### 1. Test Isolation
- Each test gets its own in-memory database
- Use transactions that rollback after each test
- Never share data between tests

### 2. Fixture Dependencies
```python
# Correct fixture dependency order
@pytest.fixture(name="engine")
def engine_fixture(): ...

@pytest.fixture(name="session")
def session_fixture(engine): ...  # Depends on engine

@pytest.fixture(name="client")
def client_fixture(engine, session): ...  # Depends on both

@pytest.fixture(name="sample_user")
def sample_user_fixture(session): ...  # Depends on session
```

### 3. Service vs Router Testing

**Service Tests** (Direct function calls):
```python
async def test_create_user_service(session):
    user_data = UserCreate(name="Test User")
    user = await user_service.create_user(user_data, session)
    assert user.name == "Test User"
```

**Router Tests** (HTTP requests):
```python
async def test_create_user_router(client: TestClient, session: Session):
    user_data = {"name": "Test User"}
    response = client.post("/user/", json=user_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

### 4. Database Engine Configuration

```python
# conftest.py
@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    # In-memory SQLite with thread safety
    engine = create_engine(
        "sqlite:///:memory:", 
        echo=True,  # Enable SQL logging for debugging
        connect_args={"check_same_thread": False}  # Allow multi-threading
    )
    
    # Configure app to use test engine
    set_test_engine(engine)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    set_test_engine(None)
```

### 5. Dependency Override Pattern

```python
# conftest.py
@pytest.fixture(name="client")
def client_fixture(engine, session):
    app = FastAPI(lifespan=lifespan)
    app.include_router(user.router)
    app.include_router(shoppinglist.router)
    app.include_router(userlistpermission.router)

    # Override dependencies
    def get_session_override():
        yield session

    app.dependency_overrides[db.get_session] = get_session_override
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
```

## Test Structure

### 1. Model Tests
Test database models and relationships directly:
```python
def test_user_model(session):
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    assert user.id is not None
    assert user.name == "Test User"
```

### 2. Service Tests
Test business logic functions:
```python
async def test_get_user_by_id(session):
    # Setup
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Test
    retrieved_user = await user_service.get_user_by_id(user.id, session)
    
    # Assert
    assert retrieved_user.id == user.id
    assert retrieved_user.name == user.name
```

### 3. Router Tests
Test HTTP endpoints:
```python
async def test_get_user_by_id(client: TestClient, session: Session):
    # Setup
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Test
    response = client.get(f"/user/{user.id}")
    
    # Assert
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == user.id
    assert user_data["name"] == user.name
```

## Troubleshooting

### "No such table" Errors

**Symptoms:**
```
sqlite3.OperationalError: no such table: user
```

**Causes:**
1. Test engine not properly set
2. Tables not created for test engine
3. Session isolation issues
4. Using production app instead of test app

**Solutions:**
1. Ensure `set_test_engine(engine)` is called
2. Call `SQLModel.metadata.create_all(engine)` after engine creation
3. Use shared session between fixtures
4. Use client fixture, not module-level TestClient

### Session Conflicts

**Symptoms:**
- Data created in test not visible to HTTP requests
- Inconsistent test results
- Transaction rollback issues

**Solutions:**
1. Use connection-based sessions with explicit transactions
2. Share the same session instance between fixtures
3. Properly override FastAPI dependencies

### Import Errors

**Symptoms:**
```
ImportError: cannot import name 'app' from 'app.main'
```

**Solutions:**
1. Don't import the production app in test files
2. Create fresh app instances in fixtures
3. Use proper dependency injection

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_user_router.py -v

# Run specific test
python -m pytest tests/test_user_router.py::test_get_users -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## Environment Variables

Set testing environment variables in `conftest.py`:
```python
import os
os.environ["TESTING"] = "1"
```

This helps distinguish between test and production environments in your application code.

## Summary

The key to successful FastAPI + SQLModel testing is:

1. **Proper session management** - Share sessions between fixtures and app
2. **Correct dependency injection** - Override production dependencies with test versions
3. **Test isolation** - Each test gets its own database
4. **Fixture organization** - Proper dependency order and cleanup
5. **Avoid module-level clients** - Always use fixture-provided test clients

Following these patterns will ensure reliable, fast, and maintainable tests for your FastAPI applications.

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, ShoppingList, UserListPermission

@pytest.mark.asyncio
async def test_get_users(client: TestClient, session: Session):
    """Test getting all users."""
    # Create test users
    user1 = User(name="User 1", hashed_password="hashed_password_1")
    user2 = User(name="User 2", hashed_password="hashed_password_2")
    session.add(user1)
    session.add(user2)
    session.commit()
    
    # Test getting all users
    response = client.get("/user/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert users[0]["name"] in ["User 1", "User 2"]
    assert users[1]["name"] in ["User 1", "User 2"]

@pytest.mark.asyncio
async def test_get_users_empty(client: TestClient, session: Session):
    """Test getting all users when no users exist."""
    # Test getting all users when none exist
    response = client.get("/user/")
    assert response.status_code == 404
    assert response.json()["detail"] == "No users found"

@pytest.mark.asyncio
async def test_get_user_by_id(client: TestClient, session: Session):
    """Test getting a user by ID."""
    # Create a test user
    user = User(name="Test User", hashed_password="hashed_test_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test getting the user by ID
    response = client.get(f"/user/{user.id}")
    assert response.status_code == 200
    retrieved_user = response.json()
    assert retrieved_user["id"] == user.id
    assert retrieved_user["name"] == user.name

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: TestClient):
    """Test getting a user by ID when user doesn't exist."""
    # Test getting a user that doesn't exist
    response = client.get("/user/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_create_user(client: TestClient, session: Session):
    """Test creating a new user."""
    # Test creating a user
    user_data = {"name": "New User", "password": "secure_password"}
    response = client.post("/user/", json=user_data)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["id"] is not None
    assert created_user["name"] == "New User"
    
    # Verify the user was saved to the database
    retrieved_user = session.get(User, created_user["id"])
    assert retrieved_user is not None
    assert retrieved_user.name == "New User"

@pytest.mark.asyncio
async def test_update_user(client: TestClient, session: Session):
    """Test updating a user."""
    # Create a test user
    user = User(name="Original Name", hashed_password="hashed_original_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test updating the user
    updated_data = {"name": "Updated Name", "password": "new_secure_password"}
    response = client.patch(f"/user/{user.id}", json=updated_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user.id
    assert updated_user["name"] == "Updated Name"
    
    # Verify the user was updated in the database
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_user_not_found(client: TestClient):
    """Test updating a user that doesn't exist."""
    # Test updating a user that doesn't exist
    updated_data = {"name": "Updated Name", "password": "new_secure_password"}
    response = client.patch("/user/999", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_user(client: TestClient, session: Session):
    """Test deleting a user."""
    # Create a test user
    user = User(name="User to Delete", hashed_password="hashed_delete_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test deleting the user
    response = client.delete(f"/user/{user.id}")
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "User deleted successfully"}
    
    # Verify the user was deleted from the database
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is None

@pytest.mark.asyncio
async def test_delete_user_not_found(client: TestClient):
    """Test deleting a user that doesn't exist."""
    # Test deleting a user that doesn't exist
    response = client.delete("/user/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_get_user_lists(client: TestClient, session: Session):
    """Test getting lists for a user."""
    # Create a user and shopping lists
    user = User(name="Test User", hashed_password="hashed_list_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    list1 = ShoppingList(name="List 1")
    list2 = ShoppingList(name="List 2")
    session.add(list1)
    session.add(list2)
    session.commit()
    session.refresh(list1)
    session.refresh(list2)
    
    # Ensure the ids are not None
    assert list1.id is not None
    assert list2.id is not None
    
    # Create permissions linking the user to the lists
    permission1 = UserListPermission(user_id=user.id, list_id=list1.id)
    permission2 = UserListPermission(user_id=user.id, list_id=list2.id)
    session.add(permission1)
    session.add(permission2)
    session.commit()
    
    # Test getting the user's lists
    response = client.get(f"/user/{user.id}/lists")
    assert response.status_code == 200
    user_lists = response.json()
    
    # Verify the lists were retrieved correctly
    assert len(user_lists) == 2
    list_names = [lst["name"] for lst in user_lists]
    assert "List 1" in list_names
    assert "List 2" in list_names

@pytest.mark.asyncio
async def test_get_user_lists_empty(client: TestClient, session: Session):
    """Test getting lists for a user when they have no lists."""
    # Create a user with no lists
    user = User(name="Test User", hashed_password="hashed_empty_list_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test getting the user's lists
    response = client.get(f"/user/{user.id}/lists")
    assert response.status_code == 200
    user_lists = response.json()
    
    # Verify an empty list is returned
    assert user_lists == []

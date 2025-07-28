import pytest
from fastapi import HTTPException
from sqlmodel import Session
from app.models import User, UserCreate, ShoppingList
from app.service import user as user_service

@pytest.mark.asyncio
async def test_get_all_users(session):
    """Test getting all users when users exist."""
    # Create test users
    user1 = User(name="User 1")
    user2 = User(name="User 2")
    session.add(user1)
    session.add(user2)
    session.commit()
    
    # Test getting all users
    users = await user_service.get_all_users(session)
    assert len(users) == 2
    assert users[0].name in ["User 1", "User 2"]
    assert users[1].name in ["User 1", "User 2"]

@pytest.mark.asyncio
async def test_get_all_users_empty(session):
    """Test getting all users when no users exist."""
    # Test getting all users when none exist
    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_all_users(session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No users found"

@pytest.mark.asyncio
async def test_get_user_by_id(session):
    """Test getting a user by ID."""
    # Create a test user
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test getting the user by ID
    retrieved_user = await user_service.get_user_by_id(user.id, session)
    assert retrieved_user.id == user.id
    assert retrieved_user.name == user.name

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(session):
    """Test getting a user by ID when user doesn't exist."""
    # Test getting a user that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_user_by_id(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_create_user(session):
    """Test creating a new user."""
    # Create a user creation object
    user_create = UserCreate(name="New User")
    
    # Test creating a user
    created_user = await user_service.create_user(user_create, session)
    
    # Verify the user was created correctly
    assert created_user.id is not None
    assert created_user.name == "New User"
    
    # Verify the user was saved to the database
    retrieved_user = session.get(User, created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.name == "New User"

@pytest.mark.asyncio
async def test_delete_user(session):
    """Test deleting a user."""
    # Create a test user
    user = User(name="User to Delete")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test deleting the user
    result = await user_service.delete_user(user.id, session)
    
    # Verify the result
    assert result == {"detail": "User deleted successfully"}
    
    # Verify the user was deleted from the database
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is None

@pytest.mark.asyncio
async def test_delete_user_not_found(session):
    """Test deleting a user that doesn't exist."""
    # Test deleting a user that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_user(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_update_user(session):
    """Test updating a user."""
    # Create a test user
    user = User(name="Original Name")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test updating the user
    user_update = UserCreate(name="Updated Name")
    updated_user = await user_service.update_user(user.id, user_update, session)
    
    # Verify the user was updated correctly
    assert updated_user.id == user.id
    assert updated_user.name == "Updated Name"
    
    # Verify the user was updated in the database
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_user_not_found(session):
    """Test updating a user that doesn't exist."""
    # Test updating a user that doesn't exist
    user_update = UserCreate(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(999, user_update, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_get_user_lists(session):
    """Test getting lists for a user."""
    # Create a user and shopping lists
    user = User(name="Test User")
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
    from app.models import UserListPermission
    permission1 = UserListPermission(user_id=user.id, list_id=list1.id)
    permission2 = UserListPermission(user_id=user.id, list_id=list2.id)
    session.add(permission1)
    session.add(permission2)
    session.commit()
    
    # Test getting the user's lists
    user_lists = await user_service.get_user_lists(user.id, session)
    
    # Verify the lists were retrieved correctly
    assert len(user_lists) == 2
    list_names = [lst.name for lst in user_lists]
    assert "List 1" in list_names
    assert "List 2" in list_names

@pytest.mark.asyncio
async def test_get_user_lists_empty(session):
    """Test getting lists for a user when they have no lists."""
    # Create a user with no lists
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test getting the user's lists
    user_lists = await user_service.get_user_lists(user.id, session)
    
    # Verify an empty list is returned
    assert user_lists == []

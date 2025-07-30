import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, ShoppingList, UserListPermission, ShoppingItem

@pytest.mark.asyncio
async def test_user_can_access_items_from_permitted_list(client: TestClient, session: Session):
    """Test that a user can access items from a list they have permission to access."""
    # Create a user and a shopping list
    from app.service.auth import hash_string_password
    hashed_password = hash_string_password("testpassword")
    user = User(name="Test User", hashed_password=hashed_password)
    shopping_list = ShoppingList(name="Test List")
    session.add(user)
    session.add(shopping_list)
    session.commit()
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Ensure the ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Create a permission linking the user to the list
    permission = UserListPermission(user_id=user.id, list_id=shopping_list.id)
    session.add(permission)
    session.commit()
    
    # Create a shopping item in the list
    item = ShoppingItem(name="Test Item", quantity=2, parent_list_id=shopping_list.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Ensure the item id is not None
    assert item.id is not None
    
    # TODO: Implement actual permission checking in the API
    # This test would check that the user can access the item
    # For now, we're just setting up the test structure

@pytest.mark.asyncio
async def test_user_cannot_access_items_from_non_permitted_list(client: TestClient, session: Session):
    """Test that a user cannot access items from a list they don't have permission to access."""
    # Create two users
    from app.service.auth import hash_string_password
    hashed_password = hash_string_password("testpassword")
    user1 = User(name="User 1", hashed_password=hashed_password)
    user2 = User(name="User 2", hashed_password=hashed_password)
    shopping_list = ShoppingList(name="Test List")
    session.add(user1)
    session.add(user2)
    session.add(shopping_list)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)
    session.refresh(shopping_list)
    
    # Ensure the ids are not None
    assert user1.id is not None
    assert user2.id is not None
    assert shopping_list.id is not None
    
    # Create a permission linking only user1 to the list
    permission = UserListPermission(user_id=user1.id, list_id=shopping_list.id)
    session.add(permission)
    session.commit()
    
    # Create a shopping item in the list
    item = ShoppingItem(name="Test Item", quantity=2, parent_list_id=shopping_list.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Ensure the item id is not None
    assert item.id is not None
    
    # TODO: Implement actual permission checking in the API
    # This test would check that user2 cannot access the item
    # For now, we're just setting up the test structure

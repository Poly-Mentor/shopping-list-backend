import pytest
from fastapi import HTTPException
from app.models import User, ShoppingList, UserListPermission
from app.service import userlistpermission as userlistpermission_service

@pytest.mark.asyncio
async def test_user_has_access_to_list(session):
    """Test checking if a user has access to a list."""
    # Create a user and a shopping list
    user = User(name="Test User")
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
    
    # Test checking if the user has access to the list
    has_access = await userlistpermission_service.user_has_access_to_list(user.id, shopping_list.id, session)
    assert has_access is True

@pytest.mark.asyncio
async def test_user_has_access_to_list_no_permission(session):
    """Test checking if a user has access to a list when they don't have permission."""
    # Create a user and a shopping list without linking them
    user = User(name="Test User")
    shopping_list = ShoppingList(name="Test List")
    session.add(user)
    session.add(shopping_list)
    session.commit()
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Ensure the ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Test checking if the user has access to the list
    has_access = await userlistpermission_service.user_has_access_to_list(user.id, shopping_list.id, session)
    assert has_access is False

@pytest.mark.asyncio
async def test_grant_access_to_list(session):
    """Test granting access to a list."""
    # Create a user and a shopping list
    user = User(name="Test User")
    shopping_list = ShoppingList(name="Test List")
    session.add(user)
    session.add(shopping_list)
    session.commit()
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Ensure the ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Test granting access to the list
    result = await userlistpermission_service.grant_access_to_list(user.id, shopping_list.id, session)
    
    # Verify the result
    assert result == {"detail": "Access granted"}
    
    # Verify the permission was created in the database
    retrieved_permission = session.get(UserListPermission, (user.id, shopping_list.id))
    assert retrieved_permission is not None
    assert retrieved_permission.user_id == user.id
    assert retrieved_permission.list_id == shopping_list.id

@pytest.mark.asyncio
async def test_grant_access_to_list_user_not_found(session):
    """Test granting access to a list when the user doesn't exist."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test granting access to a non-existent user
    with pytest.raises(HTTPException) as exc_info:
        await userlistpermission_service.grant_access_to_list(999, shopping_list.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_grant_access_to_list_list_not_found(session):
    """Test granting access to a list when the list doesn't exist."""
    # Create a user
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test granting access to a non-existent list
    with pytest.raises(HTTPException) as exc_info:
        await userlistpermission_service.grant_access_to_list(user.id, 999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "List not found"

@pytest.mark.asyncio
async def test_revoke_access_to_list(session):
    """Test revoking access to a list."""
    # Create a user and a shopping list
    user = User(name="Test User")
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
    
    # Test revoking access to the list
    result = await userlistpermission_service.revoke_access_to_list(user.id, shopping_list.id, session)
    
    # Verify the result
    assert result == {"detail": "Permission deleted successfully"}
    
    # Verify the permission was deleted from the database
    retrieved_permission = session.get(UserListPermission, (user.id, shopping_list.id))
    assert retrieved_permission is None

@pytest.mark.asyncio
async def test_revoke_access_to_list_not_found(session):
    """Test revoking access to a list when the permission doesn't exist."""
    # Create a user and a shopping list without linking them
    user = User(name="Test User")
    shopping_list = ShoppingList(name="Test List")
    session.add(user)
    session.add(shopping_list)
    session.commit()
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Ensure the ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Test revoking access when no permission exists
    with pytest.raises(HTTPException) as exc_info:
        await userlistpermission_service.revoke_access_to_list(user.id, shopping_list.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Permission not found"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, ShoppingList, UserListPermission

@pytest.mark.asyncio
async def test_check_user_list_permission(client: TestClient, session: Session):
    """Test checking if a user has access to a list."""
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
    
    # Test checking if the user has access to the list
    response = client.get("/listperm/check", params={"user_id": user.id, "list_id": shopping_list.id})
    assert response.status_code == 200
    has_access = response.json()
    assert has_access is True

@pytest.mark.asyncio
async def test_check_user_list_permission_no_permission(client: TestClient, session: Session):
    """Test checking if a user has access to a list when they don't have permission."""
    # Create a user and a shopping list without linking them
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
    
    # Test checking if the user has access to the list
    response = client.get("/listperm/check", params={"user_id": user.id, "list_id": shopping_list.id})
    assert response.status_code == 200
    has_access = response.json()
    assert has_access is False

@pytest.mark.asyncio
async def test_grant_user_list_permission(client: TestClient, session: Session):
    """Test granting access to a list."""
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
    
    # Test granting access to the list
    response = client.post("/listperm/", params={"user_id": user.id, "list_id": shopping_list.id})
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "Access granted"}
    
    # Verify the permission was created in the database
    retrieved_permission = session.get(UserListPermission, (user.id, shopping_list.id))
    assert retrieved_permission is not None
    assert retrieved_permission.user_id == user.id
    assert retrieved_permission.list_id == shopping_list.id

@pytest.mark.asyncio
async def test_grant_user_list_permission_user_not_found(client: TestClient, session: Session):
    """Test granting access to a list when the user doesn't exist."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test granting access to a non-existent user
    response = client.post("/listperm/", params={"user_id": 999, "list_id": shopping_list.id})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_grant_user_list_permission_list_not_found(client: TestClient, session: Session):
    """Test granting access to a list when the list doesn't exist."""
    # Create a user
    from app.service.auth import hash_string_password
    hashed_password = hash_string_password("testpassword")
    user = User(name="Test User", hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Ensure the id is not None
    assert user.id is not None
    
    # Test granting access to a non-existent list
    response = client.post("/listperm/", params={"user_id": user.id, "list_id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "List not found"

@pytest.mark.asyncio
async def test_revoke_user_list_permission(client: TestClient, session: Session):
    """Test revoking access to a list."""
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
    
    # Test revoking access to the list
    response = client.delete("/listperm/", params={"user_id": user.id, "list_id": shopping_list.id})
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "Permission deleted successfully"}
    
    # Verify the permission was deleted from the database
    retrieved_permission = session.get(UserListPermission, (user.id, shopping_list.id))
    assert retrieved_permission is None

@pytest.mark.asyncio
async def test_revoke_user_list_permission_not_found(client: TestClient, session: Session):
    """Test revoking access to a list when the permission doesn't exist."""
    # Create a user and a shopping list without linking them
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
    
    # Test revoking access when no permission exists
    response = client.delete("/listperm/", params={"user_id": user.id, "list_id": shopping_list.id})
    assert response.status_code == 404
    assert response.json()["detail"] == "Permission not found"

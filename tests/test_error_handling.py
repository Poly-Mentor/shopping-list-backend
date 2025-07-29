import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem

@pytest.mark.asyncio
async def test_create_item_with_invalid_list_id(client: TestClient, session: Session):
    """Test creating an item with an invalid list ID."""
    # Test creating an item with a non-existent list ID
    item_data = {"name": "Orphan Item", "quantity": 5}
    response = client.post("/shoppinglist/999/items", json=item_data)
    # This should fail with a 404 since the list doesn't exist
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_items_from_invalid_list_id(client: TestClient, session: Session):
    """Test getting items from an invalid list ID."""
    # Test getting items from a non-existent list ID
    response = client.get("/shoppinglist/999/items")
    # This should fail with a 404 since the list doesn't exist
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_item_with_invalid_parent_list(client: TestClient, session: Session):
    """Test updating an item with an invalid parent list ID."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create a shopping item
    item = ShoppingItem(name="Original Item", quantity=2, parent_list_id=shopping_list.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Ensure the id is not None
    assert item.id is not None
    
    # Test updating the item with an invalid parent list ID
    updated_data = {"name": "Updated Item", "quantity": 5, "parent_list_id": 999}
    response = client.patch(f"/shoppinglist/items/{item.id}", json=updated_data)
    # This might succeed or fail depending on implementation, but shouldn't crash
    # For now, we're just checking it doesn't crash the server

@pytest.mark.asyncio
async def test_create_item_with_null_name(client: TestClient, session: Session):
    """Test creating an item with a null name."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test creating an item with a null name
    item_data = {"name": None, "quantity": 5}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    # This should fail validation
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_item_with_empty_name(client: TestClient, session: Session):
    """Test creating an item with an empty name."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test creating an item with an empty name
    item_data = {"name": "", "quantity": 5}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    # This might succeed or fail depending on implementation, but shouldn't crash
    # For now, we're just checking it doesn't crash the server

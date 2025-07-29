import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem

@pytest.mark.asyncio
async def test_update_item(client: TestClient, session: Session):
    """Test updating a shopping item."""
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
    
    # Test updating the item
    updated_data = {"name": "Updated Item", "quantity": 5, "parent_list_id": shopping_list.id}
    response = client.patch(f"/shoppinglist/items/{item.id}", json=updated_data)
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["id"] == item.id
    assert updated_item["name"] == "Updated Item"
    assert updated_item["quantity"] == 5
    assert updated_item["parent_list_id"] == shopping_list.id
    
    # Verify the item was updated in the database
    retrieved_item = session.get(ShoppingItem, item.id)
    assert retrieved_item is not None
    assert retrieved_item.name == "Updated Item"
    assert retrieved_item.quantity == 5

@pytest.mark.asyncio
async def test_update_item_not_found(client: TestClient):
    """Test updating a shopping item that doesn't exist."""
    # Test updating an item that doesn't exist
    updated_data = {"name": "Updated Item", "quantity": 5, "parent_list_id": 1}
    response = client.patch("/shoppinglist/items/999", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

@pytest.mark.asyncio
async def test_delete_item(client: TestClient, session: Session):
    """Test deleting a shopping item."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create a shopping item
    item = ShoppingItem(name="Item to Delete", quantity=3, parent_list_id=shopping_list.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Ensure the id is not None
    assert item.id is not None
    
    # Test deleting the item
    response = client.delete(f"/shoppinglist/items/{item.id}")
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "Item deleted successfully"}
    
    # Verify the item was deleted from the database
    retrieved_item = session.get(ShoppingItem, item.id)
    assert retrieved_item is None

@pytest.mark.asyncio
async def test_delete_item_not_found(client: TestClient):
    """Test deleting a shopping item that doesn't exist."""
    # Test deleting an item that doesn't exist
    response = client.delete("/shoppinglist/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

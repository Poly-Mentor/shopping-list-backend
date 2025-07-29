import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem

@pytest.mark.asyncio
async def test_create_item_with_zero_quantity(client: TestClient, session: Session):
    """Test creating an item with zero quantity (should fail validation)."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test creating an item with zero quantity
    item_data = {"name": "Invalid Item", "quantity": 0}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    # This should fail validation
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_item_with_negative_quantity(client: TestClient, session: Session):
    """Test creating an item with negative quantity (should fail validation)."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test creating an item with negative quantity
    item_data = {"name": "Invalid Item", "quantity": -5}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    # This should fail validation
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_item_without_name(client: TestClient, session: Session):
    """Test creating an item without a name (should fail validation)."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test creating an item without a name
    item_data = {"quantity": 5}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    # This should fail validation
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_item_with_zero_quantity(client: TestClient, session: Session):
    """Test updating an item with zero quantity (should fail validation)."""
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
    
    # Test updating the item with zero quantity
    updated_data = {"name": "Updated Item", "quantity": 0, "parent_list_id": shopping_list.id}
    response = client.patch(f"/shoppinglist/items/{item.id}", json=updated_data)
    # This should fail validation
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_item_with_negative_quantity(client: TestClient, session: Session):
    """Test updating an item with negative quantity (should fail validation)."""
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
    
    # Test updating the item with negative quantity
    updated_data = {"name": "Updated Item", "quantity": -5, "parent_list_id": shopping_list.id}
    response = client.patch(f"/shoppinglist/items/{item.id}", json=updated_data)
    # This should fail validation
    assert response.status_code == 422

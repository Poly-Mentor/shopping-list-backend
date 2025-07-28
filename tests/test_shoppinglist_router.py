import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem, User, UserListPermission

@pytest.mark.asyncio
async def test_get_shopping_lists(client: TestClient, session: Session):
    """Test getting all shopping lists."""
    # Create test shopping lists
    list1 = ShoppingList(name="List 1")
    list2 = ShoppingList(name="List 2")
    session.add(list1)
    session.add(list2)
    session.commit()
    
    # Test getting all lists
    response = client.get("/shoppinglist/")
    assert response.status_code == 200
    lists = response.json()
    assert len(lists) == 2
    assert lists[0]["name"] in ["List 1", "List 2"]
    assert lists[1]["name"] in ["List 1", "List 2"]

@pytest.mark.asyncio
async def test_get_shopping_lists_empty(client: TestClient, session: Session):
    """Test getting all shopping lists when no lists exist."""
    # Test getting all lists when none exist
    response = client.get("/shoppinglist/")
    assert response.status_code == 404
    assert response.json()["detail"] == "No lists found"

@pytest.mark.asyncio
async def test_get_shopping_list_by_id(client: TestClient, session: Session):
    """Test getting a shopping list by ID."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test getting the list by ID
    response = client.get(f"/shoppinglist/{shopping_list.id}")
    assert response.status_code == 200
    retrieved_list = response.json()
    assert retrieved_list["id"] == shopping_list.id
    assert retrieved_list["name"] == shopping_list.name

@pytest.mark.asyncio
async def test_get_shopping_list_by_id_not_found(client: TestClient):
    """Test getting a shopping list by ID when list doesn't exist."""
    # Test getting a list that doesn't exist
    response = client.get("/shoppinglist/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "List not found"

@pytest.mark.asyncio
async def test_create_shopping_list(client: TestClient, session: Session):
    """Test creating a new shopping list."""
    # Test creating a list
    list_data = {"name": "New List"}
    response = client.post("/shoppinglist/", json=list_data)
    assert response.status_code == 200
    created_list = response.json()
    assert created_list["id"] is not None
    assert created_list["name"] == "New List"
    
    # Verify the list was saved to the database
    retrieved_list = session.get(ShoppingList, created_list["id"])
    assert retrieved_list is not None
    assert retrieved_list.name == "New List"

@pytest.mark.asyncio
async def test_update_shopping_list(client: TestClient, session: Session):
    """Test updating a shopping list."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="Original Name")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test updating the list
    updated_data = {"name": "Updated Name"}
    response = client.patch(f"/shoppinglist/{shopping_list.id}", json=updated_data)
    assert response.status_code == 200
    updated_list = response.json()
    assert updated_list["id"] == shopping_list.id
    assert updated_list["name"] == "Updated Name"
    
    # Verify the list was updated in the database
    retrieved_list = session.get(ShoppingList, shopping_list.id)
    assert retrieved_list is not None
    assert retrieved_list.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_shopping_list_not_found(client: TestClient):
    """Test updating a shopping list that doesn't exist."""
    # Test updating a list that doesn't exist
    updated_data = {"name": "Updated Name"}
    response = client.patch("/shoppinglist/999", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "List not found"

@pytest.mark.asyncio
async def test_delete_shopping_list(client: TestClient, session: Session):
    """Test deleting a shopping list."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="List to Delete")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test deleting the list
    response = client.delete(f"/shoppinglist/{shopping_list.id}")
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "List deleted successfully"}
    
    # Verify the list was deleted from the database
    retrieved_list = session.get(ShoppingList, shopping_list.id)
    assert retrieved_list is None

@pytest.mark.asyncio
async def test_delete_shopping_list_not_found(client: TestClient):
    """Test deleting a shopping list that doesn't exist."""
    # Test deleting a list that doesn't exist
    response = client.delete("/shoppinglist/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "List not found"

@pytest.mark.asyncio
async def test_get_items_from_list(client: TestClient, session: Session):
    """Test getting items from a shopping list."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create shopping items
    item1 = ShoppingItem(name="Item 1", quantity=2, parent_list_id=shopping_list.id)
    item2 = ShoppingItem(name="Item 2", quantity=3, parent_list_id=shopping_list.id)
    session.add(item1)
    session.add(item2)
    session.commit()
    session.refresh(item1)
    session.refresh(item2)
    
    # Test getting items from the list
    response = client.get(f"/shoppinglist/{shopping_list.id}/items")
    assert response.status_code == 200
    items = response.json()
    
    # Verify the items were retrieved correctly
    assert len(items) == 2
    item_names = [item["name"] for item in items]
    assert "Item 1" in item_names
    assert "Item 2" in item_names

@pytest.mark.asyncio
async def test_get_items_from_list_empty(client: TestClient, session: Session):
    """Test getting items from a shopping list when it has no items."""
    # Create a shopping list with no items
    shopping_list = ShoppingList(name="Empty List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test getting items from the list
    response = client.get(f"/shoppinglist/{shopping_list.id}/items")
    assert response.status_code == 200
    items = response.json()
    
    # Verify an empty list is returned
    assert items == []

@pytest.mark.asyncio
async def test_add_item(client: TestClient, session: Session):
    """Test adding an item to a shopping list."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test adding an item to the list
    item_data = {"name": "New Item", "quantity": 5}
    response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
    assert response.status_code == 200
    added_item = response.json()
    assert added_item["id"] is not None
    assert added_item["name"] == "New Item"
    assert added_item["quantity"] == 5
    assert added_item["parent_list_id"] == shopping_list.id
    
    # Verify the item was saved to the database
    retrieved_item = session.get(ShoppingItem, added_item["id"])
    assert retrieved_item is not None
    assert retrieved_item.name == "New Item"
    assert retrieved_item.quantity == 5
    assert retrieved_item.parent_list_id == shopping_list.id

import pytest
from fastapi import HTTPException
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem, ShoppingItemCreate
from app.service import shoppinglist as shoppinglist_service

@pytest.mark.asyncio
async def test_get_all_lists(session):
    """Test getting all shopping lists when lists exist."""
    # Create test shopping lists
    list1 = ShoppingList(name="List 1")
    list2 = ShoppingList(name="List 2")
    session.add(list1)
    session.add(list2)
    session.commit()
    
    # Test getting all lists
    lists = await shoppinglist_service.get_all_lists(session)
    assert len(lists) == 2
    assert lists[0].name in ["List 1", "List 2"]
    assert lists[1].name in ["List 1", "List 2"]

@pytest.mark.asyncio
async def test_get_all_lists_empty(session):
    """Test getting all shopping lists when no lists exist."""
    # Test getting all lists when none exist
    with pytest.raises(HTTPException) as exc_info:
        await shoppinglist_service.get_all_lists(session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No lists found"

@pytest.mark.asyncio
async def test_get_list_by_id(session):
    """Test getting a shopping list by ID."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test getting the list by ID
    retrieved_list = await shoppinglist_service.get_list_by_id(shopping_list.id, session)
    assert retrieved_list.id == shopping_list.id
    assert retrieved_list.name == shopping_list.name

@pytest.mark.asyncio
async def test_get_list_by_id_not_found(session):
    """Test getting a shopping list by ID when list doesn't exist."""
    # Test getting a list that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        await shoppinglist_service.get_list_by_id(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "List not found"

@pytest.mark.asyncio
async def test_create_list(session):
    """Test creating a new shopping list."""
    # Create a shopping list creation object
    from app.models import BaseShoppingList
    list_create = BaseShoppingList(name="New List")
    
    # Test creating a list
    created_list = await shoppinglist_service.create_list(list_create, session)
    
    # Verify the list was created correctly
    assert created_list.id is not None
    assert created_list.name == "New List"
    
    # Verify the list was saved to the database
    retrieved_list = session.get(ShoppingList, created_list.id)
    assert retrieved_list is not None
    assert retrieved_list.name == "New List"

@pytest.mark.asyncio
async def test_update_list(session):
    """Test updating a shopping list."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="Original Name")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test updating the list
    # Create a ShoppingList object with the updated data
    list_update = ShoppingList(name="Updated Name")
    updated_list = await shoppinglist_service.update_list(shopping_list.id, list_update, session)
    
    # Verify the list was updated correctly
    assert updated_list.id == shopping_list.id
    assert updated_list.name == "Updated Name"
    
    # Verify the list was updated in the database
    retrieved_list = session.get(ShoppingList, shopping_list.id)
    assert retrieved_list is not None
    assert retrieved_list.name == "Updated Name"

@pytest.mark.asyncio
async def test_update_list_not_found(session):
    """Test updating a shopping list that doesn't exist."""
    # Test updating a list that doesn't exist
    from app.models import ShoppingList as ShoppingListModel
    list_update = ShoppingListModel(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        await shoppinglist_service.update_list(999, list_update, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "List not found"

@pytest.mark.asyncio
async def test_delete_list(session):
    """Test deleting a shopping list."""
    # Create a test shopping list
    shopping_list = ShoppingList(name="List to Delete")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test deleting the list
    result = await shoppinglist_service.delete_list(shopping_list.id, session)
    
    # Verify the result
    assert result == {"detail": "List deleted successfully"}
    
    # Verify the list was deleted from the database
    retrieved_list = session.get(ShoppingList, shopping_list.id)
    assert retrieved_list is None

@pytest.mark.asyncio
async def test_delete_list_not_found(session):
    """Test deleting a shopping list that doesn't exist."""
    # Test deleting a list that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        await shoppinglist_service.delete_list(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "List not found"

@pytest.mark.asyncio
async def test_get_items_from_list(session):
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
    items = await shoppinglist_service.get_items_from_list(shopping_list.id, session)
    
    # Verify the items were retrieved correctly
    assert len(items) == 2
    item_names = [item.name for item in items]
    assert "Item 1" in item_names
    assert "Item 2" in item_names

@pytest.mark.asyncio
async def test_get_items_from_list_empty(session):
    """Test getting items from a shopping list when it has no items."""
    # Create a shopping list with no items
    shopping_list = ShoppingList(name="Empty List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Test getting items from the list
    items = await shoppinglist_service.get_items_from_list(shopping_list.id, session)
    
    # Verify an empty list is returned
    assert items == []

@pytest.mark.asyncio
async def test_add_item(session):
    """Test adding an item to a shopping list."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create an item to add
    from app.models import ShoppingItemCreate
    item_create = ShoppingItemCreate(name="New Item", quantity=5)
    
    # Test adding the item to the list
    added_item = await shoppinglist_service.add_item(shopping_list.id, item_create, session)
    
    # Verify the item was added correctly
    assert added_item.id is not None
    assert added_item.name == "New Item"
    assert added_item.quantity == 5
    assert added_item.parent_list_id == shopping_list.id
    
    # Verify the item was saved to the database
    retrieved_item = session.get(ShoppingItem, added_item.id)
    assert retrieved_item is not None
    assert retrieved_item.name == "New Item"
    assert retrieved_item.quantity == 5
    assert retrieved_item.parent_list_id == shopping_list.id

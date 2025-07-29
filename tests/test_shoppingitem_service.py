import pytest
from fastapi import HTTPException
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem
from app.service import shoppingitem as shoppingitem_service

@pytest.mark.asyncio
async def test_get_item_by_id(session):
    """Test getting a shopping item by ID."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create a shopping item
    item = ShoppingItem(name="Test Item", quantity=5, parent_list_id=shopping_list.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    
    # Ensure the id is not None
    assert item.id is not None
    
    # Test getting the item by ID
    retrieved_item = await shoppingitem_service.get_item_by_id(item.id, session)
    assert retrieved_item.id == item.id
    assert retrieved_item.name == item.name
    assert retrieved_item.quantity == item.quantity
    assert retrieved_item.parent_list_id == shopping_list.id

@pytest.mark.asyncio
async def test_get_item_by_id_not_found(session):
    """Test getting a shopping item by ID when item doesn't exist."""
    # Test getting an item that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        await shoppingitem_service.get_item_by_id(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"

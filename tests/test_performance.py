import pytest
import time
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem

@pytest.mark.asyncio
async def test_create_many_items_performance(client: TestClient, session: Session):
    """Test the performance of creating many items in a list."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Performance Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create many items and measure time
    start_time = time.time()
    num_items = 100
    
    for i in range(num_items):
        item_data = {"name": f"Item {i}", "quantity": i + 1}
        response = client.post(f"/shoppinglist/{shopping_list.id}/items", json=item_data)
        assert response.status_code == 200
        item = response.json()
        assert item["id"] is not None
        assert item["name"] == f"Item {i}"
        assert item["quantity"] == i + 1
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Check that it took less than 5 seconds (adjust as needed)
    assert elapsed_time < 5.0, f"Creating {num_items} items took {elapsed_time:.2f} seconds"
    
    # Verify all items were created
    response = client.get(f"/shoppinglist/{shopping_list.id}/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == num_items

@pytest.mark.asyncio
async def test_get_many_items_performance(client: TestClient, session: Session):
    """Test the performance of retrieving many items from a list."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Performance Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure the id is not None
    assert shopping_list.id is not None
    
    # Create many items
    num_items = 100
    for i in range(num_items):
        item = ShoppingItem(name=f"Item {i}", quantity=i + 1, parent_list_id=shopping_list.id)
        session.add(item)
    
    session.commit()
    
    # Measure time to retrieve all items
    start_time = time.time()
    response = client.get(f"/shoppinglist/{shopping_list.id}/items")
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    
    # Check that it took less than 1 second (adjust as needed)
    assert elapsed_time < 1.0, f"Retrieving {num_items} items took {elapsed_time:.2f} seconds"
    
    # Verify all items were retrieved
    assert response.status_code == 200
    items = response.json()
    assert len(items) == num_items

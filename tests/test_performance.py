import pytest
import time
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import ShoppingList, ShoppingItem, User
from app.service.auth import hash_string_password, create_access_token

def get_auth_headers(user: User) -> dict:
    """Helper function to get authentication headers for a user."""
    access_token = create_access_token(user)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.mark.asyncio
async def test_create_many_items_performance(client: TestClient, session: Session):
    """Test the performance of creating many items in a list."""
    # Create a user for authentication
    hashed_password = hash_string_password("testpassword")
    user = User(name="Performance Test User", hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Get authentication headers
    headers = get_auth_headers(user)

    # Create a shopping list
    list_data = {"name": "Performance Test List"}
    response = client.post("/shoppinglist/", json=list_data, headers=headers)
    assert response.status_code == 200
    shopping_list = response.json()

    # Create many items and measure time
    start_time = time.time()
    num_items = 100

    for i in range(num_items):
        item_data = {"name": f"Item {i}", "quantity": i + 1}
        response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item_data, headers=headers)
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
    response = client.get(f"/shoppinglist/{shopping_list['id']}/items", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == num_items

@pytest.mark.asyncio
async def test_get_many_items_performance(client: TestClient, session: Session):
    """Test the performance of retrieving many items from a list."""
    # Create a user for authentication
    hashed_password = hash_string_password("testpassword")
    user = User(name="Performance Test User 2", hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    # Get authentication headers
    headers = get_auth_headers(user)

    # Create a shopping list
    list_data = {"name": "Performance Test List"}
    response = client.post("/shoppinglist/", json=list_data, headers=headers)
    assert response.status_code == 200
    shopping_list = response.json()

    # Create many items
    num_items = 100
    for i in range(num_items):
        item_data = {"name": f"Item {i}", "quantity": i + 1}
        response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item_data, headers=headers)
        assert response.status_code == 200

    # Measure time to retrieve all items
    start_time = time.time()
    response = client.get(f"/shoppinglist/{shopping_list['id']}/items", headers=headers)
    end_time = time.time()

    elapsed_time = end_time - start_time

    # Check that it took less than 1 second (adjust as needed)
    assert elapsed_time < 1.0, f"Retrieving {num_items} items took {elapsed_time:.2f} seconds"

    # Verify all items were retrieved
    assert response.status_code == 200
    items = response.json()
    assert len(items) == num_items

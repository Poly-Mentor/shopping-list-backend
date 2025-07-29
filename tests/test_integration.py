import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, ShoppingList, UserListPermission, ShoppingItem

@pytest.mark.asyncio
async def test_full_user_workflow(client: TestClient, session: Session):
    """Test a full workflow: create user, create list, add items, retrieve everything."""
    # Create a user
    user_data = {"name": "Integration Test User"}
    response = client.post("/user/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] is not None
    assert user["name"] == "Integration Test User"
    
    # Create a shopping list
    list_data = {"name": "Integration Test List"}
    response = client.post("/shoppinglist/", json=list_data)
    assert response.status_code == 200
    shopping_list = response.json()
    assert shopping_list["id"] is not None
    assert shopping_list["name"] == "Integration Test List"
    
    # Grant user access to the list
    response = client.post("/listperm/", params={"user_id": user["id"], "list_id": shopping_list["id"]})
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "Access granted"}
    
    # Add items to the list
    item1_data = {"name": "Milk", "quantity": 2}
    response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item1_data)
    assert response.status_code == 200
    item1 = response.json()
    assert item1["id"] is not None
    assert item1["name"] == "Milk"
    assert item1["quantity"] == 2
    
    item2_data = {"name": "Bread", "quantity": 1}
    response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item2_data)
    assert response.status_code == 200
    item2 = response.json()
    assert item2["id"] is not None
    assert item2["name"] == "Bread"
    assert item2["quantity"] == 1
    
    # Retrieve the list with items
    response = client.get(f"/shoppinglist/{shopping_list['id']}")
    assert response.status_code == 200
    retrieved_list = response.json()
    assert retrieved_list["id"] == shopping_list["id"]
    assert retrieved_list["name"] == "Integration Test List"
    
    # Retrieve items from the list
    response = client.get(f"/shoppinglist/{shopping_list['id']}/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    item_names = [item["name"] for item in items]
    assert "Milk" in item_names
    assert "Bread" in item_names
    
    # Retrieve user lists
    response = client.get(f"/user/{user['id']}/lists")
    assert response.status_code == 200
    user_lists = response.json()
    assert len(user_lists) == 1
    assert user_lists[0]["id"] == shopping_list["id"]
    assert user_lists[0]["name"] == "Integration Test List"

@pytest.mark.asyncio
async def test_cascade_delete_workflow(client: TestClient, session: Session):
    """Test that deleting a list cascades to its items and permissions."""
    # Create a user
    user_data = {"name": "Cascade Test User"}
    response = client.post("/user/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    
    # Create a shopping list
    list_data = {"name": "Cascade Test List"}
    response = client.post("/shoppinglist/", json=list_data)
    assert response.status_code == 200
    shopping_list = response.json()
    
    # Grant user access to the list
    response = client.post("/listperm/", params={"user_id": user["id"], "list_id": shopping_list["id"]})
    assert response.status_code == 200
    
    # Add items to the list
    item1_data = {"name": "Milk", "quantity": 2}
    response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item1_data)
    assert response.status_code == 200
    item1 = response.json()
    
    item2_data = {"name": "Bread", "quantity": 1}
    response = client.post(f"/shoppinglist/{shopping_list['id']}/items", json=item2_data)
    assert response.status_code == 200
    item2 = response.json()
    
    # Verify items exist in the database
    retrieved_item1 = session.get(ShoppingItem, item1["id"])
    retrieved_item2 = session.get(ShoppingItem, item2["id"])
    assert retrieved_item1 is not None
    assert retrieved_item2 is not None
    
    # Verify permission exists
    permission = session.get(UserListPermission, (user["id"], shopping_list["id"]))
    assert permission is not None
    
    # Delete the shopping list
    response = client.delete(f"/shoppinglist/{shopping_list['id']}")
    assert response.status_code == 200
    result = response.json()
    assert result == {"detail": "List deleted successfully"}
    
    # Verify the list was deleted
    response = client.get(f"/shoppinglist/{shopping_list['id']}")
    assert response.status_code == 404
    
    # Verify items were deleted (cascade delete)
    retrieved_item1 = session.get(ShoppingItem, item1["id"])
    retrieved_item2 = session.get(ShoppingItem, item2["id"])
    assert retrieved_item1 is None
    assert retrieved_item2 is None
    
    # Verify permission was deleted (cascade delete)
    permission = session.get(UserListPermission, (user["id"], shopping_list["id"]))
    assert permission is None

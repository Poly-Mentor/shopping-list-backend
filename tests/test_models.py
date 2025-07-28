import pytest
from sqlmodel import Session, select
from app.models import User, ShoppingList, UserListPermission, ShoppingItem

def test_user_model(session):
    """Test User model creation and persistence."""
    # Create a user
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Verify the user was saved correctly
    assert user.id is not None
    assert user.name == "Test User"
    
    # Retrieve the user from the database
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.name == "Test User"

def test_shopping_list_model(session):
    """Test ShoppingList model creation and persistence."""
    # Create a shopping list
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Verify the shopping list was saved correctly
    assert shopping_list.id is not None
    assert shopping_list.name == "Test List"
    
    # Retrieve the shopping list from the database
    retrieved_list = session.get(ShoppingList, shopping_list.id)
    assert retrieved_list is not None
    assert retrieved_list.name == "Test List"

def test_user_list_permission_model(session):
    """Test UserListPermission model creation and persistence."""
    # First create a user and a shopping list
    user = User(name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    shopping_list = ShoppingList(name="Test List")
    session.add(shopping_list)
    session.commit()
    session.refresh(shopping_list)
    
    # Ensure ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Create a permission linking the user to the list
    permission = UserListPermission(user_id=user.id, list_id=shopping_list.id)
    session.add(permission)
    session.commit()
    
    # Verify the permission was saved correctly
    retrieved_permission = session.get(UserListPermission, (user.id, shopping_list.id))
    assert retrieved_permission is not None
    assert retrieved_permission.user_id == user.id
    assert retrieved_permission.list_id == shopping_list.id

def test_shopping_item_model(session):
    """Test ShoppingItem model creation and persistence."""
    # First create a shopping list
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
    
    # Verify the item was saved correctly
    assert item.id is not None
    assert item.name == "Test Item"
    assert item.quantity == 5
    assert item.parent_list_id == shopping_list.id
    
    # Retrieve the item from the database
    retrieved_item = session.get(ShoppingItem, item.id)
    assert retrieved_item is not None
    assert retrieved_item.name == "Test Item"
    assert retrieved_item.quantity == 5
    assert retrieved_item.parent_list_id == shopping_list.id

def test_user_shopping_list_relationship(session):
    """Test the many-to-many relationship between User and ShoppingList."""
    # Create a user and a shopping list
    user = User(name="Test User")
    shopping_list = ShoppingList(name="Test List")
    session.add(user)
    session.add(shopping_list)
    session.commit()
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Ensure ids are not None
    assert user.id is not None
    assert shopping_list.id is not None
    
    # Link them through UserListPermission
    permission = UserListPermission(user_id=user.id, list_id=shopping_list.id)
    session.add(permission)
    session.commit()
    
    # Verify the relationship
    # Refresh the objects to get the latest state
    session.refresh(user)
    session.refresh(shopping_list)
    
    # Check that the relationships are established
    assert user.lists is not None
    assert len(user.lists) == 1
    assert user.lists[0].id == shopping_list.id
    
    assert shopping_list.users is not None
    assert len(shopping_list.users) == 1
    assert shopping_list.users[0].id == user.id

def test_shopping_list_items_relationship(session):
    """Test the one-to-many relationship between ShoppingList and ShoppingItem."""
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
    
    # Verify the relationship
    session.refresh(shopping_list)
    
    # Check that the items are associated with the list
    assert shopping_list.items is not None
    assert len(shopping_list.items) == 2
    
    # Check that items have the correct parent list
    assert item1.parent_list_id == shopping_list.id
    assert item2.parent_list_id == shopping_list.id

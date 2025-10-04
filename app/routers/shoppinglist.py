from fastapi import APIRouter, Depends
from app.models import ShoppingList, ShoppingListCreate, ShoppingItem, ShoppingItemCreate, User
from app.data.db import DBSessionDep
import app.service.shoppinglist
import app.service.shoppingitem

from app.service.user import get_current_user

router = APIRouter(prefix="/shoppinglist")

# Operations on whole lists

@router.get("/")
async def get_shopping_lists(
    shopping_lists: list[ShoppingList] = Depends(app.service.shoppinglist.get_all_lists)
) -> list[ShoppingList]:
    """Fetch all shopping lists."""
    return shopping_lists
    

@router.get("/{list_id}")
async def get_shopping_list_by_id(
    list_id : int, 
    shopping_list: ShoppingList = Depends(app.service.shoppinglist.get_list_by_id)
) -> ShoppingList:
    """Fetch a shopping list by ID."""
    return shopping_list

@router.post("/")
async def create_shopping_list(
    session: DBSessionDep,
    new_list_data: ShoppingListCreate, 
    user: User = Depends(get_current_user)
) -> ShoppingList:
    """Create a new shopping list."""
    return await app.service.shoppinglist.create_list(new_list_data, user, session)

@router.patch("/{list_id}")
async def update_shopping_list(
    list_id : int,
    new_list_data: ShoppingListCreate,
    session: DBSessionDep,
    user: User = Depends(get_current_user)
) -> ShoppingList:
    """Update existing shopping list."""
    updated_list = await app.service.shoppinglist.update_list(list_id=list_id, new_list_data=new_list_data, user=user, session=session)
    return updated_list

@router.delete("/{list_id}")
async def delete_shopping_list(
    list_id: int,
    session: DBSessionDep,
    user: User = Depends(get_current_user)
) -> dict:
    """Delete a shopping list by ID."""
    deleting_result: dict = await app.service.shoppinglist.delete_list(list_id=list_id, user=user, session=session)
    return deleting_result

# Operations on list items

@router.get("/{list_id}/items")
async def get_items_from_list(
    list_id: int,
    session: DBSessionDep,
    user: User = Depends(get_current_user)
) -> list[ShoppingItem]:
    result = await app.service.shoppinglist.get_items_from_list(list_id=list_id, session=session, user=user)
    return result

@router.post("/{list_id}/items")
async def add_item(
    list_id: int,
    input_item: ShoppingItemCreate,
    session: DBSessionDep,
    user: User = Depends(get_current_user)
) -> ShoppingItem:
    new_item = await app.service.shoppinglist.add_item(list_id=list_id, user=user, input_item=input_item, session=session)
    return new_item

# Operations on individual items

# TODO add authentication and permissions checks
@router.patch("/items/{item_id}")
async def update_item(
    item_id: int,
    item_data: ShoppingItem,
    updated_item: ShoppingItem = Depends(app.service.shoppingitem.update_item)
) -> ShoppingItem:
    return updated_item

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    result: dict = Depends(app.service.shoppingitem.delete_item)
) -> dict:
    return result

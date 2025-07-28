from fastapi import APIRouter, Depends
from models import ShoppingList, ShoppingListCreate, ShoppingItem
import service.shoppinglist
import service.shoppingitem

router = APIRouter(prefix="/shoppinglist")

# Operations on whole lists

@router.get("/")
async def get_shopping_lists(
    shopping_lists: list[ShoppingList] = Depends(service.shoppinglist.get_all_lists)
) -> list[ShoppingList]:
    """Fetch all shopping lists."""
    return shopping_lists

@router.get("/{list_id}")
async def get_shopping_list_by_id(
    list_id : int, 
    shopping_list: ShoppingList = Depends(service.shoppinglist.get_list_by_id)
) -> ShoppingList:
    """Fetch a shopping list by ID."""
    return shopping_list

@router.post("/")
async def create_shopping_list(
    new_list_data: ShoppingListCreate, 
    new_shopping_list: ShoppingList = Depends(service.shoppinglist.create_list)
) -> ShoppingList:
    """Create a new shopping list."""
    return new_shopping_list

@router.patch("/{list_id}")
async def update_shopping_list(
    list_id : int,
    new_list_data: ShoppingListCreate,
    updated_list: ShoppingList = Depends(service.shoppinglist.update_list)
) -> ShoppingList:
    """Update existing shopping list."""
    return updated_list

@router.delete("/{list_id}")
async def delete_shopping_list(
    list_id: int,
    deleting_result: dict = Depends(service.shoppinglist.delete_list)
) -> dict:
    """Delete a shopping list by ID."""
    return deleting_result

# Operations on list items

@router.get("/{list_id}/items")
async def get_items_from_list(
    list_id: int,
    result = Depends(service.shoppinglist.get_items_from_list)
) -> list[ShoppingItem]:
    return result

@router.post("/{list_id}/items")
async def add_item(
    list_id: int,
    new_item: ShoppingItem = Depends(service.shoppinglist.add_item)
) -> ShoppingItem:
    return new_item
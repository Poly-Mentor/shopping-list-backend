from models import *
from data import db
from sqlmodel import Session, select
from fastapi import Depends, HTTPException

async def get_all_lists(session: Session = Depends(db.get_session)) -> list[ShoppingList]:
    """Fetch all lists from the database."""
    lists: list[ShoppingList] = list(session.exec(select(ShoppingList)).all())
    if not lists:
        raise HTTPException(status_code=404, detail="No lists found")
    return lists

async def get_list_by_id(list_id: int, session: Session = Depends(db.get_session)) -> ShoppingList:
    """Fetch a list by ID from the database."""
    shopping_list = session.get(ShoppingList, list_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="List not found")
    return shopping_list

async def create_list(new_list_data: BaseShoppingList, session: Session = Depends(db.get_session)) -> ShoppingList:
    """Create a new list in the database."""
    new_list = ShoppingList(name=new_list_data.name)
    session.add(new_list)
    session.commit()
    session.refresh(new_list)
    return new_list

async def update_list(list_id: int, new_list_data: ShoppingList, session: Session = Depends(db.get_session)) -> ShoppingList:
    """Update existing list in the database."""
    existing_list = await get_list_by_id(list_id, session)
    if new_list_data.name is not None:
        existing_list.name = new_list_data.name
    session.add(existing_list)
    session.commit()
    session.refresh(existing_list)
    return existing_list
    

async def delete_list(list_id: int, session: Session = Depends(db.get_session)) -> dict:
    """Delete list and its items from the database."""
    shopping_list = await get_list_by_id(list_id, session)
    # permissions and child items are deleted automatically (ondelete="CASCADE")
    session.delete(shopping_list)
    session.commit()
    return {"detail": "List deleted successfully"}

# Item operations

async def get_items_from_list(list_id: int, session: Session = Depends(db.get_session)) -> list[ShoppingItem]:
    shoppinglist = await get_list_by_id(list_id, session)
    if not shoppinglist.items:
        return []
    return shoppinglist.items

async def add_item(
        list_id: int,
        input_item: ShoppingItemCreate,
        session: Session = Depends(db.get_session)
) -> ShoppingItem:
    parent_list = await get_list_by_id(list_id, session)
    if not parent_list.items:
        parent_list.items = []
    ShoppingItemCreate.model_validate(input_item)
    init_data = input_item.model_dump()
    init_data.update({"parent_list_id" : parent_list.id})
    new_item = ShoppingItem(**init_data)
    parent_list.items.append
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item

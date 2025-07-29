from fastapi import HTTPException
from app.models import ShoppingItem, ShoppingList, BaseShoppingItem
from app.data.db import DBSessionDep

async def get_item_by_id(item_id: int, session: DBSessionDep) -> ShoppingItem:
    item = session.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

async def update_item(item_id: int, item_data: BaseShoppingItem, session: DBSessionDep) -> ShoppingItem:
    item = await get_item_by_id(item_id, session)
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

async def delete_item(item_id: int, session: DBSessionDep) -> dict:
    item = await get_item_by_id(item_id, session)
    session.delete(item)
    session.commit()
    return {"detail": "Item deleted successfully"}

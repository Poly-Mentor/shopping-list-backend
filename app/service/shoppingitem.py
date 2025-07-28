from fastapi import HTTPException
from models import ShoppingItem, ShoppingList
from data.db import DBSessionDep

async def get_item_by_id(item_id: int, session: DBSessionDep) -> ShoppingItem:
    item = session.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
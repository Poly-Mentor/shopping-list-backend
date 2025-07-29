from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.models import UserListPermission, User, ShoppingList
from app.service.user import get_user_by_id
from app.service.shoppinglist import get_list_by_id
from app.data.db import DBSessionDep

async def user_has_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> bool:
    found_permission: UserListPermission | None = session.exec(
        select(UserListPermission).where(UserListPermission.user_id == user_id, UserListPermission.list_id == list_id)
        ).first()
    
    return found_permission is not None
    

async def grant_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> dict:
    ### Wrong way: it is possible to add new permission with invalid user_id and list_id ! #####
    # new_permission: UserListPermission = UserListPermission(user_id=user_id, list_id=list_id)
    # db_permission = new_permission.model_validate(new_permission)
    # session.add(db_permission)
    # session.commit()
    # session.refresh(db_permission)
    ############################################################################################

    # below coroutines will raise exception when ID is invalid
    user = await get_user_by_id(user_id, session)
    shopping_list = await get_list_by_id(list_id, session)

    if user.lists is None:
        user.lists = []
    user.lists.append(shopping_list)
    session.add(user)
    session.commit()

    return {"detail": "Access granted"}

async def revoke_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> dict:
    permission_to_delete = session.get(UserListPermission, (user_id, list_id))
    if not permission_to_delete:
        raise HTTPException(status_code=404, detail="Permission not found")
    session.delete(permission_to_delete)
    session.commit()
    return {"detail": "Permission deleted successfully"}

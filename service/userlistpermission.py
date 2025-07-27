from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from data import db
from models.userlistpermission import UserListPermission

DBSessionDep = Annotated[Session, Depends(db.get_session)]

async def user_has_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> bool:
    found_permission: UserListPermission | None = session.exec(
        select(UserListPermission).where(UserListPermission.user_id == user_id, UserListPermission.list_id == list_id)
        ).first()
    return found_permission is not None

async def grant_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> UserListPermission:
    new_permission: UserListPermission = UserListPermission(user_id=user_id, list_id=list_id)
    # TODO BUG add validation, it is possible to add new permission with invalid user_id and list_id !
    session.add(new_permission)
    session.commit()
    session.refresh(new_permission)
    return new_permission

async def revoke_access_to_list(user_id: int, list_id: int, session: DBSessionDep) -> dict:
    permission_to_delete: UserListPermission | None = session.exec(
        select(UserListPermission).where(
            UserListPermission.user_id == user_id,
            UserListPermission.list_id == list_id)).first()
    if not permission_to_delete:
        raise HTTPException(status_code=404, detail="Permission not found")
    session.delete(permission_to_delete)
    session.commit()
    return {"detail": "Permission deleted successfully"}

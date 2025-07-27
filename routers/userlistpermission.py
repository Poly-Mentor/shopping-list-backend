from fastapi import APIRouter, Depends
from models import UserListPermission
import service.userlistpermission

router = APIRouter(prefix="/listperm")

@router.get("/check")
async def check_user_list_permission(
    user_id: int,
    list_id: int,
    has_access: bool = Depends(service.userlistpermission.user_has_access_to_list)
) -> bool:
    return has_access

@router.post("/")
async def grant_user_list_permission(
    user_id: int,
    list_id: int,
    created_permission: UserListPermission = Depends(service.userlistpermission.grant_access_to_list)
) -> UserListPermission:
    return created_permission

@router.delete("/")
async def revoke_user_list_permission(
    user_id: int,
    list_id: int,
    result: dict = Depends(service.userlistpermission.revoke_access_to_list)
) -> dict:
    return result
    
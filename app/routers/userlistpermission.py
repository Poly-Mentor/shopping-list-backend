from fastapi import APIRouter, Depends
import app.service.userlistpermission

router = APIRouter(prefix="/listperm")

@router.get("/check")
async def check_user_list_permission(
    user_id: int,
    list_id: int,
    has_access: bool = Depends(app.service.userlistpermission.user_has_access_to_list)
) -> bool:
    return has_access

@router.post("/")
async def grant_user_list_permission(
    user_id: int,
    list_id: int,
    result: dict = Depends(app.service.userlistpermission.grant_access_to_list)
) -> dict:
    return result

@router.delete("/")
async def revoke_user_list_permission(
    user_id: int,
    list_id: int,
    result: dict = Depends(app.service.userlistpermission.revoke_access_to_list)
) -> dict:
    return result

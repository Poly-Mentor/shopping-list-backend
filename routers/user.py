from fastapi import APIRouter, Depends
from models.user import User, UserCreate
import service.user

router = APIRouter(prefix="/user")

@router.get("/")
async def get_users(users: list[User] = Depends(service.user.get_all_users)) -> list[User]:
    """Fetch all users."""
    return users

@router.get("/{user_id}")
async def get_user_by_id(user_id : int, user: User = Depends(service.user.get_user_by_id) ) -> User:
    """Fetch a user by ID."""
    return user

@router.post("/")
async def create_user(new_user_data: UserCreate, newUser : User = Depends(service.user.create_user)) -> User:
    """Create a new user."""
    return newUser

@router.patch("/{user_id}")
async def update_user(user_id: int, userAfterUpdate : User = Depends(service.user.update_user)) -> User:
    """Update an existing user."""
    return userAfterUpdate

@router.delete("/{user_id}")
async def delete_user(user_id: int, deletingResult : dict = Depends(service.user.delete_user)) -> dict:
    return deletingResult

from fastapi import APIRouter, Depends
from app.models import User, UserCreate, ShoppingList
import app.service.user

router = APIRouter(prefix="/user")

@router.get("/")
async def get_users(users: list[User] = Depends(app.service.user.get_all_users)) -> list[User]:
    """Fetch all users."""
    return users

@router.get("/{user_id}")
async def get_user_by_id(user_id : int, user: User = Depends(app.service.user.get_user_by_id) ) -> User:
    """Fetch a user by ID."""
    return user

@router.get("/{user_id}/lists", response_model=list[ShoppingList])
async def get_user_lists(user_id : int, users_lists: list[ShoppingList] = Depends(app.service.user.get_user_lists) ) -> list[ShoppingList]:
    """Fetch a list of shopping lists to which user of given ID has access to."""
    return users_lists

@router.post("/")
async def create_user(new_user_data: UserCreate, newUser : User = Depends(app.service.user.create_user)) -> User:
    """Create a new user."""
    return newUser

@router.patch("/{user_id}")
async def update_user(user_id: int, userAfterUpdate : User = Depends(app.service.user.update_user)) -> User:
    """Update an existing user."""
    return userAfterUpdate

@router.delete("/{user_id}")
async def delete_user(user_id: int, deletingResult : dict = Depends(app.service.user.delete_user)) -> dict:
    return deletingResult

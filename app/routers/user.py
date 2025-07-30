from fastapi import APIRouter, Depends, HTTPException
from app.models import User, UserCreate, ShoppingList, Token
from sqlmodel import Session

import app.service.user
import app.service.auth
from app.data.db import get_session
from app.service.auth import verify_password, oauth2_form_dep

router = APIRouter(prefix="/user")


@router.get("/")
async def get_users(users: list[User] = Depends(app.service.user.get_all_users)) -> list[User]:
    """Fetch all users."""
    return users

@router.get("/me")
async def get_current_user(current_user: User = Depends(app.service.user.get_current_user)) -> User:
    return current_user

@router.get("/{user_id}")
async def get_user_by_id(user_id : int, user: User = Depends(app.service.user.get_user_by_id) ) -> User:
    """Fetch a user by ID."""
    return user

@router.get("/{user_id}/lists", response_model=list[ShoppingList])
async def get_user_lists(user_id : int, users_lists: list[ShoppingList] = Depends(app.service.user.get_user_lists) ) -> list[ShoppingList]:
    """Fetch a list of shopping lists to which user of given ID has access to."""
    return users_lists

@router.post("/")
async def create_user(user: UserCreate, newUser : User = Depends(app.service.user.create_user)) -> User:
    """Create a new user."""
    return newUser

@router.patch("/{user_id}")
async def update_user(user_id: int, userAfterUpdate : User = Depends(app.service.user.update_user)) -> User:
    """Update an existing user."""
    return userAfterUpdate

@router.delete("/{user_id}")
async def delete_user(user_id: int, deletingResult : dict = Depends(app.service.user.delete_user)) -> dict:
    return deletingResult

@router.post("/auth", response_model=Token)
async def login_for_access_token(
    form_data: oauth2_form_dep,
    session: Session = Depends(get_session)
) -> Token:
    user = await app.service.user.get_user_from_login(form_data, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return Token(access_token=app.service.auth.create_access_token(user), token_type="bearer")

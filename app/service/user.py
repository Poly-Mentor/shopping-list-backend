from models import User, UserCreate, ShoppingList
from data import db
from sqlmodel import Session, select
from fastapi import Depends, HTTPException


async def get_all_users(session: Session = Depends(db.get_session)) -> list[User]:
    """Fetch all users from the database."""
    users: list[User] = list(session.exec(select(User)).all())
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

async def get_user_by_id(user_id: int, session: Session = Depends(db.get_session)) -> User:
    """Fetch a user by ID from the database."""
    # user = session.exec(select(User).where(User.id == user_id)).first()
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def create_user(new_user_data: UserCreate, session: Session = Depends(db.get_session)) -> User:
    """Create a new user in the database."""
    new_user = User(name=new_user_data.name)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

async def delete_user(user_id: int, session: Session = Depends(db.get_session)) -> dict:
    """Delete a user by ID from the database."""
    user: User | None = await get_user_by_id(user_id, session)
    # related permissions are being deleted automatically ondelete="CASCADE"
    session.delete(user)
    session.commit()
    return {"detail": "User deleted successfully"}

async def update_user(user_id: int, updatedUser: UserCreate, session: Session = Depends(db.get_session)) -> User:
    """Update an existing user in the database."""
    existing_user = await get_user_by_id(user_id, session)
    
    if updatedUser.name is not None:
        existing_user.name = updatedUser.name
    
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user

async def get_user_lists(user_id: int, session: Session = Depends(db.get_session)) -> list[ShoppingList]:
    user: User = await get_user_by_id(user_id, session)
    if user.lists is None:
        return []
    return user.lists
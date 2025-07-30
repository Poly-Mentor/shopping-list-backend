import jwt
from fastapi import Depends, HTTPException, status
from app.models import User, UserCreate, ShoppingList
from app.data import db
from sqlmodel import Session, select
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.service.auth import hash_password_dep, decode_token, oauth2_scheme, SECRET_KEY, ALGORITHM, verify_password

oauth2_pwd_scheme = oauth2_scheme

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

async def get_user_by_name(username: str, session: Session = Depends(db.get_session)) -> User:
    user = session.exec(select(User).where(User.name == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user_from_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(db.get_session)
) -> User | None:
    user = session.exec(select(User).where(User.name == form_data.username)).first()
    if user and verify_password(form_data.password, user.hashed_password):
        return user
    return None

async def get_current_user(
    token: str = Depends(oauth2_pwd_scheme),
    session: Session = Depends(db.get_session)
) -> User:
    # Decode token directly without using the dependency function
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    user = session.exec(select(User).where(User.name == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def create_user(
        user: UserCreate,
        hashed_password: hash_password_dep,
        session: Session = Depends(db.get_session)
) -> User:
    """Create a new user in the database."""
    new_user = User(name=user.name, hashed_password=hashed_password)
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

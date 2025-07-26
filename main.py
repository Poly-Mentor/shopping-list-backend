from os import getenv
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

from models.user import *
from sqlmodel import Session, select
from data import db

if getenv("ENVIRONMENT") == "development":
    load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # things to do before the app starts
    db.create_db_and_tables()
    yield
    # Cleanup actions can be added here if needed


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/user/")
async def get_user(session: Session = Depends(db.get_session)) -> list[User]:
    users : list[User] = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@app.get("/user/{user_id}")
async def get_user(user_id : int, session: Session = Depends(db.get_session)) -> User:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user/")
async def create_user(user: UserCreate, session: Session = Depends(db.get_session)) -> User:
    newUser = User(name=user.name)
    session.add(newUser)
    session.commit()
    session.refresh(newUser)
    return newUser

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(db.get_session)) -> dict:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"detail": "User deleted successfully"}

@app.patch("/user/{user_id}")
async def update_user(user_id: int, updatedUser: UserCreate, session: Session = Depends(db.get_session)) -> User:
    existing_user = session.exec(select(User).where(User.id == user_id)).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if updatedUser.name is not None:
        existing_user.name = updatedUser.name
    
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=getenv("ENVIRONMENT") == "development")
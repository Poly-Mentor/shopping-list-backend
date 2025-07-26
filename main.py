from os import getenv
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

import service.user
from models.user import User, UserCreate

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
async def get_user(users: list[User] = Depends(service.user.get_all_users)) -> list[User]:
    """Fetch all users."""
    return users

@app.get("/user/{user_id}")
async def get_user(user_id : int, user: User = Depends(service.user.get_user_by_id) ) -> User:
    """Fetch a user by ID."""
    return user

@app.post("/user/")
async def create_user(user: UserCreate, newUser : User = Depends(service.user.create_user)) -> User:
    """Create a new user."""
    return newUser

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, deletingResult : dict = Depends(service.user.delete_user)) -> dict:
    return deletingResult

@app.patch("/user/{user_id}")
async def update_user(user_id: int, updatedUser: UserCreate, userAfterUpdate : User = Depends(service.user.update_user)) -> User:
    """Update an existing user."""
    return userAfterUpdate

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=getenv("ENVIRONMENT") == "development")
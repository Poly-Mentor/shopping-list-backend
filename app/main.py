from os import getenv
from dotenv import load_dotenv, find_dotenv

# Load environment variables - find_dotenv automatically searches for .env file
load_dotenv(find_dotenv(), verbose=True)

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth, user, shoppinglist, userlistpermission

from app.data import db

# TODO migrations (alembic?)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # things to do before the app starts
    # Always create tables, the test setup will handle test database creation
    db.create_db_and_tables()
    yield
    # Cleanup actions can be added here if needed


app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(shoppinglist.router)
app.include_router(userlistpermission.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

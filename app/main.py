from os import getenv
from dotenv import load_dotenv

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import user, shoppinglist, userlistpermission

from app.data import db

if getenv("ENVIRONMENT") == "development":
    load_dotenv()

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

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=getenv("ENVIRONMENT") == "development")

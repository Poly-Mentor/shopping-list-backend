from sqlmodel import SQLModel, Field

class BaseUser(SQLModel):
    name: str

class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)

class UserCreate(BaseUser):
    pass
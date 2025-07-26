from sqlmodel import SQLModel, Field

class BaseUser(SQLModel):
    name: str

class User(BaseUser, table=True):
    id: int = Field(primary_key=True)

class UserCreate(BaseUser):
    pass
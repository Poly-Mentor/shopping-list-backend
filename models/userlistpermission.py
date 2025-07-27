from sqlmodel import SQLModel, Field

class UserListPermission(SQLModel, table=True):
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    list_id: int = Field(primary_key=True, foreign_key="shoppinglist.id")
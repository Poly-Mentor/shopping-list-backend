from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

###########################################################
# ACCESS PERMISSIONS TO SHOPPING LIST (link table)
###########################################################

class UserListPermission(SQLModel, table=True):
    user_id: int = Field(primary_key=True, foreign_key="user.id", ondelete="CASCADE")
    list_id: int = Field(primary_key=True, foreign_key="shoppinglist.id", ondelete="CASCADE")

###########################################################
# USER
###########################################################

class BaseUser(SQLModel):
    name: str

class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True)
    lists: list["ShoppingList"] | None = Relationship(back_populates="users", link_model=UserListPermission)
    hashed_password: str
    # owned_lists: list["ShoppingList"] = Relationship(back_populates="owner")

class UserCreate(BaseUser):
    password: str
    pass

###########################################################
# SHOPPING LIST
###########################################################

class BaseShoppingList(SQLModel):
    name: str

class ShoppingList(BaseShoppingList, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list[User] | None = Relationship(back_populates="lists", link_model=UserListPermission)
    items: list["ShoppingItem"] | None = Relationship(back_populates="parent_list", cascade_delete=True)
    # owner_id: int = Field(foreign_key="user.id")
    # owner: User = Relationship(back_populates="owned_lists")

class ShoppingListCreate(BaseShoppingList):
    pass

###########################################################
# SHOPPING ITEM
###########################################################

class BaseShoppingItem(SQLModel):
    name: str
    quantity: int | None = Field(default=None, gt=0)
    # category

class ShoppingItem(BaseShoppingItem, table=True):
    id: int | None = Field(default=None, primary_key=True)
    parent_list_id: int = Field(foreign_key="shoppinglist.id", ondelete="CASCADE")
    parent_list: ShoppingList = Relationship(back_populates="items")

class ShoppingItemCreate(BaseShoppingItem):
    pass

###########################################################
# TOKENS
###########################################################

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
from sqlmodel import SQLModel, Field, Relationship

###########################################################
# ACCESS PERMISSIONS TO SHOPPING LIST (link table)
###########################################################

class UserListPermission(SQLModel, table=True):
    user_id: int = Field(primary_key=True, foreign_key="user.id")
    list_id: int = Field(primary_key=True, foreign_key="shoppinglist.id")

###########################################################
# USER
###########################################################

class BaseUser(SQLModel):
    name: str

class User(BaseUser, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lists: list["ShoppingList"] | None = Relationship(back_populates="users", link_model=UserListPermission)

class UserCreate(BaseUser):
    pass

###########################################################
# SHOPPING LIST
###########################################################

class BaseShoppingList(SQLModel):
    name: str

class ShoppingList(BaseShoppingList, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list[User] | None = Relationship(back_populates="lists", link_model=UserListPermission)
    items: list["ShoppingItem"] | None = Relationship(back_populates="parent_list")

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
    parent_list_id: int = Field(foreign_key="shoppinglist.id")
    parent_list: ShoppingList = Relationship(back_populates="items")

class ShoppingItemCreate(BaseShoppingItem):
    pass
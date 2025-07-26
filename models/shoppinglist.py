from sqlmodel import SQLModel, Field

class BaseShoppingList(SQLModel):
    name: str

class ShoppingList(BaseShoppingList, table=True):
    id: int = Field(primary_key=True)

class ShoppingListCreate(BaseShoppingList):
    pass

from enum import Enum
from sqlmodel import SQLModel, Field

class ProductCategories(str, Enum):
    MONITORES = "Monitores"
    MOUSES = "Mouses"
    KEYBOARD = "Keyboard"

class Product(SQLModel, table=True):
    __tablename__ = "app_inv_products"

    id: int | None = Field(primary_key=True, default=None)
    name: str
    price: float
    category: str
    quantity: int

class CreateProduct(SQLModel):
    name: str
    price: float
    category: ProductCategories
    quantity: int

class UpdateProduct(SQLModel):
    name: str | None = None
    price: float | None = None
    category: ProductCategories | None = None
    quantity: int | None = None

    
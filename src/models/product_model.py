from pydantic import BaseModel, field_validator

from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    __tablename__ = "app_inv_products"

    id: int | None = Field(primary_key=True, default=None)
    name: str
    price: float
    category: str
    quantity: int


class CreateProduct(BaseModel):
    name: str 
    price: float
    quantity: int
    category: str

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str):
        return value.strip().capitalize()


class UpdateProduct(BaseModel):
    name: str | None = None
    price: float | None = None
    quantity: int | None = None
    category: str | None = None

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str | None):
        if value is not None:
            return value.strip().capitalize()
        return value

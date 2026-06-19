from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, examples=["Wireless Mouse"])
    sku: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9]+$', examples=["WM001"])
    price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2, examples=[29.99])
    quantity_in_stock: int = Field(..., ge=0, examples=[100])


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r'^[a-zA-Z0-9]+$')
    price: Optional[Decimal] = Field(None, gt=0, max_digits=12, decimal_places=2)
    quantity_in_stock: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int
    product_name: str
    sku: str
    price: Decimal
    quantity_in_stock: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

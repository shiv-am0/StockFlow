from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$', examples=["+1234567890"])


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

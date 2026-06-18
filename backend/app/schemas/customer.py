from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    phone_number: Optional[str] = Field(None, max_length=50, examples=["+1-555-1234"])


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

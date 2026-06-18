from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.customer import CustomerCreate, CustomerListResponse, CustomerResponse
from app.schemas.common import SuccessResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.create_customer(data)


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    skip = (page - 1) * page_size
    items, total = service.get_customers(skip=skip, limit=page_size, search=search)
    return CustomerListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.get_customer(customer_id)


@router.delete("/{customer_id}", response_model=SuccessResponse)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    service.delete_customer(customer_id)
    return SuccessResponse(message="Customer deleted successfully")

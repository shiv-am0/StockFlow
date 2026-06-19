from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse, OrderStatusUpdate
from app.schemas.common import SuccessResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.create_order(data)


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    skip = (page - 1) * page_size
    items, total = service.get_orders(skip=skip, limit=page_size)
    return OrderListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.get_order(order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    return service.update_order_status(order_id, data.status)


@router.delete("/{order_id}", response_model=SuccessResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    service.delete_order(order_id)
    return SuccessResponse(message="Order deleted successfully")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.product_service import ProductService
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    product_stats = ProductService(db).get_dashboard_stats()
    customer_stats = CustomerService(db).get_dashboard_stats()
    order_stats = OrderService(db).get_dashboard_stats()
    return {**product_stats, **customer_stats, **order_stats}

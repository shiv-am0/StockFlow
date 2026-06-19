from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse
from app.utils.exceptions import BadRequestError, NotFoundError


def _build_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        customer_name=order.customer.full_name if order.customer else "Unknown",
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.product_name if item.product else "Unknown",
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in (order.order_items or [])
        ],
    )


class OrderService:
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.db = db

    def create_order(self, data: OrderCreate) -> OrderResponse:
        from app.models.customer import Customer

        customer = (
            self.db.query(Customer)
            .filter(Customer.id == data.customer_id, Customer.is_deleted.is_(False))
            .first()
        )
        if not customer:
            raise NotFoundError("Customer not found")

        order = Order(customer_id=data.customer_id, total_amount=Decimal("0.00"), status="pending")
        self.db.add(order)
        self.db.flush()

        total = Decimal("0.00")

        for item_data in data.items:
            product = (
                self.db.query(Product)
                .filter(Product.id == item_data.product_id, Product.is_deleted.is_(False))
                .first()
            )
            if not product:
                self.db.rollback()
                raise NotFoundError(f"Product with id {item_data.product_id} not found")

            if product.quantity_in_stock < item_data.quantity:
                self.db.rollback()
                raise BadRequestError(
                    f"Insufficient stock for product '{product.product_name}'. "
                    f"Requested: {item_data.quantity}, Available: {product.quantity_in_stock}"
                )

            unit_price = product.price
            subtotal = unit_price * Decimal(str(item_data.quantity))
            total += subtotal

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
            self.db.add(order_item)

            product.quantity_in_stock -= item_data.quantity

        order.total_amount = total
        self.db.commit()
        self.db.refresh(order)
        full_order = self.repo.get_by_id(order.id)
        return _build_order_response(full_order)

    def get_order(self, order_id: int) -> OrderResponse:
        order = self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        return _build_order_response(order)

    def get_orders(self, skip: int = 0, limit: int = 100) -> tuple[list[OrderResponse], int]:
        items, total = self.repo.get_all(skip=skip, limit=limit)
        return [_build_order_response(o) for o in items], total

    def update_order_status(self, order_id: int, new_status: str) -> OrderResponse:
        order = self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")

        if order.status != "pending":
            raise BadRequestError(
                f"Cannot change status from '{order.status}'. Only pending orders can be updated."
            )

        if new_status == "cancelled":
            for item in order.order_items:
                product = (
                    self.db.query(Product)
                    .filter(Product.id == item.product_id)
                    .first()
                )
                if product:
                    product.quantity_in_stock += item.quantity

        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        full_order = self.repo.get_by_id(order.id)
        return _build_order_response(full_order)

    def delete_order(self, order_id: int) -> bool:
        if not self.repo.get_by_id(order_id):
            raise NotFoundError("Order not found")
        return self.repo.soft_delete(order_id)

    def get_dashboard_stats(self) -> dict:
        total_orders = self.repo.get_total_count()
        return {"total_orders": total_orders}

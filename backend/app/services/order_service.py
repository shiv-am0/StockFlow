from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate
from app.utils.exceptions import BadRequestError, NotFoundError


class OrderService:
    def __init__(self, db: Session):
        self.repo = OrderRepository(db)
        self.db = db

    def create_order(self, data: OrderCreate):
        from app.models.customer import Customer

        customer = self.db.query(Customer).filter(Customer.id == data.customer_id, Customer.is_deleted.is_(False)).first()
        if not customer:
            raise NotFoundError("Customer not found")

        order = Order(customer_id=data.customer_id, total_amount=Decimal("0.00"), status="pending")
        self.db.add(order)
        self.db.flush()

        total = Decimal("0.00")

        for item_data in data.items:
            product = self.db.query(Product).filter(Product.id == item_data.product_id, Product.is_deleted.is_(False)).first()
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
        return self.repo.get_by_id(order.id)

    def get_order(self, order_id: int):
        order = self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        return order

    def get_orders(self, skip: int = 0, limit: int = 100):
        items, total = self.repo.get_all(skip=skip, limit=limit)
        return items, total

    def delete_order(self, order_id: int):
        if not self.repo.get_by_id(order_id):
            raise NotFoundError("Order not found")
        return self.repo.soft_delete(order_id)

    def get_dashboard_stats(self):
        total_orders = self.repo.get_total_count()
        return {"total_orders": total_orders}

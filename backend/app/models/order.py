import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.session import Base


class Order(Base):
    __tablename__ = "orders"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    customer_id = sa.Column(sa.Integer, sa.ForeignKey("customers.id"), nullable=False, index=True)
    total_amount = sa.Column(sa.Numeric(14, 2), nullable=False, default=0)
    status = sa.Column(sa.String(50), nullable=False, default="pending")
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    is_deleted = sa.Column(sa.Boolean, default=False)

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, total={self.total_amount})>"

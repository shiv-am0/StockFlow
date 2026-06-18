import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.session import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey("products.id"), nullable=False, index=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    unit_price = sa.Column(sa.Numeric(12, 2), nullable=False)
    subtotal = sa.Column(sa.Numeric(14, 2), nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"

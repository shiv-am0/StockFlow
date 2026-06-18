import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.session import Base


class Product(Base):
    __tablename__ = "products"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    product_name = sa.Column(sa.String(255), nullable=False)
    sku = sa.Column(sa.String(100), unique=True, nullable=False, index=True)
    price = sa.Column(sa.Numeric(12, 2), nullable=False)
    quantity_in_stock = sa.Column(sa.Integer, nullable=False, default=0)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    is_deleted = sa.Column(sa.Boolean, default=False)

    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.product_name}, sku={self.sku})>"

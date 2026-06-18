import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.session import Base


class Customer(Base):
    __tablename__ = "customers"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    full_name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    phone_number = sa.Column(sa.String(50), nullable=True, unique=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    is_deleted = sa.Column(sa.Boolean, default=False)

    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.full_name}, email={self.email})>"

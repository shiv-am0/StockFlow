from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate
from app.utils.exceptions import ConflictError, NotFoundError


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def create_customer(self, data: CustomerCreate):
        if self.repo.exists(email=data.email):
            raise ConflictError(f"Customer with email '{data.email}' already exists")
        if data.phone_number and self.repo.exists(phone_number=data.phone_number):
            raise ConflictError(f"Customer with phone '{data.phone_number}' already exists")
        try:
            return self.repo.create(**data.model_dump())
        except IntegrityError:
            raise ConflictError("Customer with this email or phone already exists")

    def get_customer(self, customer_id: int):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer not found")
        return customer

    def get_customers(self, skip: int = 0, limit: int = 100, search: str | None = None):
        items, total = self.repo.get_all(skip=skip, limit=limit, search=search)
        return items, total

    def delete_customer(self, customer_id: int):
        if not self.repo.get_by_id(customer_id):
            raise NotFoundError("Customer not found")
        return self.repo.soft_delete(customer_id)

    def get_dashboard_stats(self):
        total_customers = self.repo.get_total_count()
        return {"total_customers": total_customers}

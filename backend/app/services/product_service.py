from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.exceptions import ConflictError, NotFoundError


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def create_product(self, data: ProductCreate):
        if self.repo.exists(sku=data.sku):
            raise ConflictError(f"Product with SKU '{data.sku}' already exists")
        try:
            return self.repo.create(**data.model_dump())
        except IntegrityError:
            raise ConflictError(f"Product with SKU '{data.sku}' already exists")

    def get_product(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    def get_products(self, skip: int = 0, limit: int = 100, search: str | None = None):
        items, total = self.repo.get_all(skip=skip, limit=limit, search=search)
        return items, total

    def update_product(self, product_id: int, data: ProductUpdate):
        product = self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        if data.sku and data.sku != product.sku and self.repo.exists(sku=data.sku):
            raise ConflictError(f"Product with SKU '{data.sku}' already exists")
        try:
            updated = self.repo.update(product_id, **data.model_dump())
            if not updated:
                raise NotFoundError("Product not found")
            return updated
        except IntegrityError:
            raise ConflictError(f"Product with SKU '{data.sku}' already exists")

    def delete_product(self, product_id: int):
        if not self.repo.get_by_id(product_id):
            raise NotFoundError("Product not found")
        return self.repo.soft_delete(product_id)

    def get_low_stock(self, threshold: int = 10):
        return self.repo.get_low_stock(threshold)

    def get_dashboard_stats(self):
        total_products = self.repo.get_total_count()
        low_stock = self.repo.get_low_stock(10)
        return {"total_products": total_products, "low_stock_count": len(low_stock), "low_stock_products": low_stock}

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_all(
        self, skip: int = 0, limit: int = 100, search: str | None = None, **filters
    ) -> tuple[list[Product], int]:
        query = self.db.query(self.model).filter(self.model.is_deleted.is_(False))

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.product_name.ilike(search_term),
                    self.model.sku.ilike(search_term),
                )
            )

        count = query.count()
        items = query.order_by(self.model.id).offset(skip).limit(limit).all()
        return items, count

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        return (
            self.db.query(self.model)
            .filter(self.model.is_deleted.is_(False), self.model.quantity_in_stock < threshold)
            .all()
        )

    def get_total_count(self) -> int:
        return self.db.query(self.model).filter(self.model.is_deleted.is_(False)).count()

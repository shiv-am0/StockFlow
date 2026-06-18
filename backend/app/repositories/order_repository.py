from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_id(self, id: int) -> Order | None:
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.customer), joinedload(self.model.order_items).joinedload(OrderItem.product))
            .filter(self.model.id == id, self.model.is_deleted.is_(False))
            .first()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100, search: str | None = None, **filters
    ) -> tuple[list[Order], int]:
        query = (
            self.db.query(self.model)
            .options(joinedload(self.model.customer))
            .filter(self.model.is_deleted.is_(False))
        )

        count = query.count()
        items = query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()
        return items, count

    def get_total_count(self) -> int:
        return self.db.query(self.model).filter(self.model.is_deleted.is_(False)).count()

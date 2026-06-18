from typing import Any, Generic, TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id, self.model.is_deleted.is_(False)).first()

    def get_all(
        self, skip: int = 0, limit: int = 100, search: str | None = None, **filters
    ) -> tuple[list[ModelType], int]:
        query = self.db.query(self.model).filter(self.model.is_deleted.is_(False))

        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, attr) == value)

        count = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, count

    def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **kwargs) -> ModelType | None:
        obj = self.get_by_id(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def soft_delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False
        obj.is_deleted = True
        self.db.commit()
        return True

    def exists(self, **kwargs) -> bool:
        query = self.db.query(self.model).filter(self.model.is_deleted.is_(False))
        for attr, value in kwargs.items():
            query = query.filter(getattr(self.model, attr) == value)
        return query.first() is not None

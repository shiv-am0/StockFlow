from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class SuccessResponse(BaseModel):
    message: str
    data: Any = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "StockFlow API"

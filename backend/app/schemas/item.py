from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.category import CategoryResponse
from app.schemas.location import LocationResponse


class ItemCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    category_id: int | None = None
    location_id: int | None = None
    quantity: int = 0
    unit: str = "pcs"
    price: Decimal | None = None
    low_stock_threshold: int = 10


class ItemUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    location_id: int | None = None
    unit: str | None = None
    price: Decimal | None = None
    low_stock_threshold: int | None = None


class ItemResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    category_id: int | None
    location_id: int | None
    quantity: int
    unit: str
    price: Decimal | None
    low_stock_threshold: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse | None = None
    location: LocationResponse | None = None

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    per_page: int
    pages: int


class RestockRequest(BaseModel):
    quantity: int
    notes: str | None = None


class WithdrawRequest(BaseModel):
    quantity: int
    notes: str | None = None

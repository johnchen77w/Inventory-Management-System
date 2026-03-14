from datetime import datetime

from pydantic import BaseModel


class LocationCreate(BaseModel):
    name: str
    description: str | None = None
    address: str | None = None


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    address: str | None = None


class LocationResponse(BaseModel):
    id: int
    name: str
    description: str | None
    address: str | None
    created_at: datetime
    item_count: int = 0

    class Config:
        from_attributes = True

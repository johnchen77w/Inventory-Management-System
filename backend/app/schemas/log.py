from datetime import datetime

from pydantic import BaseModel


class LogResponse(BaseModel):
    id: int
    item_id: int
    user_id: int
    action: str
    quantity_before: int | None
    quantity_after: int | None
    notes: str | None
    created_at: datetime
    item_name: str | None = None
    user_name: str | None = None

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    logs: list[LogResponse]
    total: int
    page: int
    per_page: int
    pages: int

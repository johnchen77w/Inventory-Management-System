from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    item_id: int
    message: str
    recipient_email: str
    is_acknowledged: bool
    acknowledged_by: int | None
    created_at: datetime
    acknowledged_at: datetime | None
    item_name: str | None = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    page: int
    per_page: int
    pages: int

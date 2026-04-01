from datetime import datetime
from pydantic import BaseModel, EmailStr


class EmailSubscriptionCreate(BaseModel):
    email: EmailStr
    notify_restock: bool = True
    notify_withdraw: bool = True
    notify_low_stock: bool = True


class EmailSubscriptionUpdate(BaseModel):
    email: EmailStr | None = None
    notify_restock: bool | None = None
    notify_withdraw: bool | None = None
    notify_low_stock: bool | None = None
    is_active: bool | None = None


class EmailSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    email: str
    notify_restock: bool
    notify_withdraw: bool
    notify_low_stock: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_name: str | None = None
    user_role: str | None = None

    class Config:
        from_attributes = True

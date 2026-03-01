import enum
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LogAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"
    restock = "restock"
    withdraw = "withdraw"


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    action: Mapped[LogAction] = mapped_column(Enum(LogAction), nullable=False)
    quantity_before: Mapped[int | None] = mapped_column(Integer)
    quantity_after: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    item: Mapped["Item"] = relationship(back_populates="inventory_logs")
    user: Mapped["User"] = relationship(back_populates="inventory_logs")

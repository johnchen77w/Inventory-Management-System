from datetime import datetime

from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True, nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acknowledged_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    item: Mapped["Item"] = relationship(back_populates="alerts")
    acknowledged_by_user: Mapped["User | None"] = relationship(foreign_keys=[acknowledged_by])

from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), index=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="pcs", nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category: Mapped["Category | None"] = relationship(back_populates="items")
    location: Mapped["Location | None"] = relationship(back_populates="items")
    inventory_logs: Mapped[list["InventoryLog"]] = relationship(back_populates="item", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="item", cascade="all, delete-orphan")

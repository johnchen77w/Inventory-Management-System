from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_items: int
    total_stock: int
    low_stock_count: int
    unacknowledged_alerts: int


class CategoryBreakdown(BaseModel):
    category_id: int | None
    category_name: str
    item_count: int
    total_quantity: int

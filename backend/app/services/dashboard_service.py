from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models.item import Item
from app.models.category import Category
from app.models.alert import Alert


def get_summary(db: Session) -> dict:
    total_items = db.query(sa_func.count(Item.id)).scalar() or 0
    total_stock = db.query(sa_func.coalesce(sa_func.sum(Item.quantity), 0)).scalar()
    low_stock_count = db.query(sa_func.count(Item.id)).filter(Item.quantity < Item.low_stock_threshold).scalar() or 0
    unacknowledged_alerts = db.query(sa_func.count(Alert.id)).filter(Alert.is_acknowledged == False).scalar() or 0

    return {
        "total_items": total_items,
        "total_stock": int(total_stock),
        "low_stock_count": low_stock_count,
        "unacknowledged_alerts": unacknowledged_alerts,
    }


def get_category_breakdown(db: Session) -> list[dict]:
    results = (
        db.query(
            Category.id,
            Category.name,
            sa_func.count(Item.id).label("item_count"),
            sa_func.coalesce(sa_func.sum(Item.quantity), 0).label("total_quantity"),
        )
        .outerjoin(Item, Item.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .all()
    )

    breakdown = []
    for row in results:
        breakdown.append({
            "category_id": row[0],
            "category_name": row[1],
            "item_count": row[2],
            "total_quantity": int(row[3]),
        })

    # Also include uncategorized items
    uncategorized = (
        db.query(
            sa_func.count(Item.id).label("item_count"),
            sa_func.coalesce(sa_func.sum(Item.quantity), 0).label("total_quantity"),
        )
        .filter(Item.category_id == None)
        .first()
    )
    if uncategorized and uncategorized[0] > 0:
        breakdown.append({
            "category_id": None,
            "category_name": "Uncategorized",
            "item_count": uncategorized[0],
            "total_quantity": int(uncategorized[1]),
        })

    return breakdown

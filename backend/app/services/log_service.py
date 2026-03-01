import math

from sqlalchemy.orm import Session, joinedload

from app.models.inventory_log import InventoryLog


def get_logs(db: Session, page: int = 1, per_page: int = 20) -> dict:
    query = db.query(InventoryLog).options(
        joinedload(InventoryLog.item), joinedload(InventoryLog.user)
    ).order_by(InventoryLog.created_at.desc())

    total = query.count()
    pages = math.ceil(total / per_page) if per_page > 0 else 1
    logs = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for log in logs:
        result.append({
            "id": log.id, "item_id": log.item_id, "user_id": log.user_id,
            "action": log.action.value, "quantity_before": log.quantity_before,
            "quantity_after": log.quantity_after, "notes": log.notes,
            "created_at": log.created_at,
            "item_name": log.item.name if log.item else None,
            "user_name": log.user.full_name if log.user else None,
        })

    return {"logs": result, "total": total, "page": page, "per_page": per_page, "pages": pages}


def get_item_logs(db: Session, item_id: int, page: int = 1, per_page: int = 20) -> dict:
    query = db.query(InventoryLog).options(
        joinedload(InventoryLog.user)
    ).filter(InventoryLog.item_id == item_id).order_by(InventoryLog.created_at.desc())

    total = query.count()
    pages = math.ceil(total / per_page) if per_page > 0 else 1
    logs = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for log in logs:
        result.append({
            "id": log.id, "item_id": log.item_id, "user_id": log.user_id,
            "action": log.action.value, "quantity_before": log.quantity_before,
            "quantity_after": log.quantity_after, "notes": log.notes,
            "created_at": log.created_at,
            "item_name": None,
            "user_name": log.user.full_name if log.user else None,
        })

    return {"logs": result, "total": total, "page": page, "per_page": per_page, "pages": pages}

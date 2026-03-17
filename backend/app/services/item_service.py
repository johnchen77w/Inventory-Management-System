import math
import anyio
from app.services.ws_manager import manager

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func, or_
from fastapi import HTTPException, status

from app.models.item import Item
from app.models.inventory_log import InventoryLog, LogAction
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    location_id: int | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
    below_threshold: bool = False,
    sort_by: str = "updated_at",
    order: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    query = db.query(Item).options(joinedload(Item.category), joinedload(Item.location))

    if search:
        query = query.filter(or_(Item.name.ilike(f"%{search}%"), Item.sku.ilike(f"%{search}%")))
    if category_id is not None:
        query = query.filter(Item.category_id == category_id)
    if location_id is not None:
        query = query.filter(Item.location_id == location_id)
    if min_quantity is not None:
        query = query.filter(Item.quantity >= min_quantity)
    if max_quantity is not None:
        query = query.filter(Item.quantity <= max_quantity)
    if below_threshold:
        query = query.filter(Item.quantity < Item.low_stock_threshold)

    # Sorting
    sort_column = getattr(Item, sort_by, Item.updated_at)
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()
    pages = math.ceil(total / per_page) if per_page > 0 else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}


def get_item(db: Session, item_id: int) -> Item:
    item = db.query(Item).options(joinedload(Item.category), joinedload(Item.location)).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


def create_item(db: Session, data: ItemCreate, user: User) -> Item:
    existing = db.query(Item).filter(Item.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")

    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    # Audit log
    log = InventoryLog(
        item_id=item.id, user_id=user.id, action=LogAction.create,
        quantity_before=0, quantity_after=item.quantity, notes="Item created",
    )
    db.add(log)
    db.commit()

    # Reload with relationships
    return get_item(db, item.id)


def update_item(db: Session, item_id: int, data: ItemUpdate, user: User) -> Item:
    item = get_item(db, item_id)
    qty_before = item.quantity
    update_data = data.model_dump(exclude_unset=True)

    if "sku" in update_data and update_data["sku"] != item.sku:
        existing = db.query(Item).filter(Item.sku == update_data["sku"], Item.id != item_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")

    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)

    log = InventoryLog(
        item_id=item.id, user_id=user.id, action=LogAction.update,
        quantity_before=qty_before, quantity_after=item.quantity, notes="Item updated",
    )
    db.add(log)
    db.commit()

    return get_item(db, item.id)


def delete_item(db: Session, item_id: int, user: User) -> None:
    item = get_item(db, item_id)
    log = InventoryLog(
        item_id=item.id, user_id=user.id, action=LogAction.delete,
        quantity_before=item.quantity, quantity_after=0, notes="Item deleted",
    )
    db.add(log)
    db.delete(item)
    db.commit()


def restock_item(db: Session, item_id: int, quantity: int, notes: str | None, user: User) -> Item:
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")

    item = get_item(db, item_id)
    qty_before = item.quantity
    item.quantity += quantity
    db.commit()

    log = InventoryLog(
        item_id=item.id, user_id=user.id, action=LogAction.restock,
        quantity_before=qty_before, quantity_after=item.quantity,
        notes=notes or f"Restocked {quantity} units",
    )
    db.add(log)
    db.commit()

    emit_ws_event({
        "type": "item_restocked",
        "item_id": item.id,
        "name": item.name,
        "quantity_before": qty_before,
        "quantity_after": item.quantity,
        "changed_by": user.id,
        "notes": notes or f"Restocked {quantity} units",
    })

    return get_item(db, item.id)


def withdraw_item(db: Session, item_id: int, quantity: int, notes: str | None, user: User) -> Item:
    if quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")

    item = get_item(db, item_id)
    if item.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {item.quantity}, requested: {quantity}",
        )

    qty_before = item.quantity
    item.quantity -= quantity
    db.commit()

    log = InventoryLog(
        item_id=item.id, user_id=user.id, action=LogAction.withdraw,
        quantity_before=qty_before, quantity_after=item.quantity,
        notes=notes or f"Withdrew {quantity} units",
    )
    db.add(log)
    db.commit()

    # Check low stock threshold
    if item.quantity < item.low_stock_threshold:
        from app.services.alert_service import trigger_low_stock_alert
        trigger_low_stock_alert(db, item)

    emit_ws_event({
        "type": "item_withdrawn",
        "item_id": item.id,
        "name": item.name,
        "quantity_before": qty_before,
        "quantity_after": item.quantity,
        "changed_by": user.id,
        "notes": notes or f"Withdrew {quantity} units",
    })

    return get_item(db, item.id)


def emit_ws_event(event: dict):
    try:
        anyio.from_thread.run(manager.broadcast, event)
    except Exception as e:
        print("WS emit error:", repr(e))


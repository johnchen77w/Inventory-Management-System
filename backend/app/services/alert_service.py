import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.alert import Alert
from app.models.item import Item
from app.models.user import User, UserRole
from app.config import settings


def trigger_low_stock_alert(db: Session, item: Item) -> None:
    # Get all manager emails
    managers = db.query(User).filter(User.role == UserRole.manager, User.is_active == True).all()
    for manager in managers:
        alert = Alert(
            item_id=item.id,
            message=f"Low stock alert: {item.name} (SKU: {item.sku}) has {item.quantity} units, below threshold of {item.low_stock_threshold}",
            recipient_email=manager.email,
        )
        db.add(alert)
    db.commit()

    # Optionally call serverless function
    if settings.low_stock_function_url:
        try:
            import httpx
            httpx.post(
                settings.low_stock_function_url,
                json={
                    "item_name": item.name,
                    "sku": item.sku,
                    "quantity": item.quantity,
                    "threshold": item.low_stock_threshold,
                    "location": item.location.name if item.location else "Unknown",
                    "recipient_emails": [m.email for m in managers],
                },
                timeout=10.0,
            )
        except Exception:
            pass  # Don't fail the main operation if serverless call fails


def get_alerts(db: Session, page: int = 1, per_page: int = 20) -> dict:
    query = db.query(Alert).options(joinedload(Alert.item)).order_by(Alert.created_at.desc())

    total = query.count()
    pages = math.ceil(total / per_page) if per_page > 0 else 1
    alerts = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for alert in alerts:
        result.append({
            "id": alert.id, "item_id": alert.item_id, "message": alert.message,
            "recipient_email": alert.recipient_email, "is_acknowledged": alert.is_acknowledged,
            "acknowledged_by": alert.acknowledged_by, "created_at": alert.created_at,
            "acknowledged_at": alert.acknowledged_at,
            "item_name": alert.item.name if alert.item else None,
        })

    return {"alerts": result, "total": total, "page": page, "per_page": per_page, "pages": pages}


def acknowledge_alert(db: Session, alert_id: int, user: User) -> dict:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    if alert.is_acknowledged:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alert already acknowledged")

    alert.is_acknowledged = True
    alert.acknowledged_by = user.id
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)

    return {
        "id": alert.id, "item_id": alert.item_id, "message": alert.message,
        "recipient_email": alert.recipient_email, "is_acknowledged": alert.is_acknowledged,
        "acknowledged_by": alert.acknowledged_by, "created_at": alert.created_at,
        "acknowledged_at": alert.acknowledged_at,
        "item_name": alert.item.name if alert.item else None,
    }

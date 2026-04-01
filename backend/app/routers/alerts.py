from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertListResponse
from app.services import alert_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def list_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    return alert_service.get_alerts(db, page=page, per_page=per_page)


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return alert_service.acknowledge_alert(db, alert_id, current_user)

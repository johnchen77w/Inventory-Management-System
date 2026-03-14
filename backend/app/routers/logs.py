from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.log import LogListResponse
from app.services import log_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("", response_model=LogListResponse)
def list_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    return log_service.get_logs(db, page=page, per_page=per_page)


@router.get("/item/{item_id}", response_model=LogListResponse)
def get_item_logs(
    item_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    return log_service.get_item_logs(db, item_id=item_id, page=page, per_page=per_page)

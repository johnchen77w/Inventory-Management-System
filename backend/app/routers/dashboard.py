from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, CategoryBreakdown
from app.services import dashboard_service
from app.middleware.auth import require_staff_or_manager

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return dashboard_service.get_summary(db)


@router.get("/category-breakdown", response_model=list[CategoryBreakdown])
def get_category_breakdown(db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return dashboard_service.get_category_breakdown(db)

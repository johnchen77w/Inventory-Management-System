from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.email_subscription import (
    EmailSubscriptionCreate,
    EmailSubscriptionUpdate,
    EmailSubscriptionResponse,
)
from app.services import email_subscription_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("/me", response_model=list[EmailSubscriptionResponse])
def get_my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    """Get current user's email subscriptions."""
    return email_subscription_service.get_my_subscriptions(db, current_user)


@router.get("", response_model=list[EmailSubscriptionResponse])
def get_all_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    """Get all email subscriptions (manager only)."""
    return email_subscription_service.get_all_subscriptions(db)


@router.post("", response_model=EmailSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    data: EmailSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    """Create a new email subscription for the current user."""
    return email_subscription_service.create_subscription(db, data, current_user)


@router.put("/{sub_id}", response_model=EmailSubscriptionResponse)
def update_subscription(
    sub_id: int,
    data: EmailSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    """Update an email subscription. Workers can only update their own."""
    return email_subscription_service.update_subscription(db, sub_id, data, current_user)


@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    """Delete an email subscription. Workers can only delete their own."""
    email_subscription_service.delete_subscription(db, sub_id, current_user)

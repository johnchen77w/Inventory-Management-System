from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.email_subscription import EmailSubscription
from app.models.user import User
from app.schemas.email_subscription import EmailSubscriptionCreate, EmailSubscriptionUpdate


def _to_response(sub: EmailSubscription) -> dict:
    return {
        "id": sub.id,
        "user_id": sub.user_id,
        "email": sub.email,
        "notify_restock": sub.notify_restock,
        "notify_withdraw": sub.notify_withdraw,
        "notify_low_stock": sub.notify_low_stock,
        "is_active": sub.is_active,
        "created_at": sub.created_at,
        "updated_at": sub.updated_at,
        "user_name": sub.user.full_name if sub.user else None,
        "user_role": sub.user.role.value if sub.user else None,
    }


def get_my_subscriptions(db: Session, user: User) -> list[dict]:
    subs = (
        db.query(EmailSubscription)
        .options(joinedload(EmailSubscription.user))
        .filter(EmailSubscription.user_id == user.id)
        .order_by(EmailSubscription.created_at.desc())
        .all()
    )
    return [_to_response(s) for s in subs]


def get_all_subscriptions(db: Session) -> list[dict]:
    subs = (
        db.query(EmailSubscription)
        .options(joinedload(EmailSubscription.user))
        .order_by(EmailSubscription.created_at.desc())
        .all()
    )
    return [_to_response(s) for s in subs]


def create_subscription(db: Session, data: EmailSubscriptionCreate, user: User) -> dict:
    existing = (
        db.query(EmailSubscription)
        .filter(EmailSubscription.user_id == user.id, EmailSubscription.email == data.email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already subscribed for your account",
        )

    sub = EmailSubscription(
        user_id=user.id,
        email=data.email,
        notify_restock=data.notify_restock,
        notify_withdraw=data.notify_withdraw,
        notify_low_stock=data.notify_low_stock,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return _to_response(
        db.query(EmailSubscription)
        .options(joinedload(EmailSubscription.user))
        .filter(EmailSubscription.id == sub.id)
        .first()
    )


def update_subscription(db: Session, sub_id: int, data: EmailSubscriptionUpdate, user: User) -> dict:
    sub = (
        db.query(EmailSubscription)
        .options(joinedload(EmailSubscription.user))
        .filter(EmailSubscription.id == sub_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    # Workers can only update their own subscriptions
    if user.role.value != "manager" and sub.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify another user's subscription")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sub, key, value)
    db.commit()
    db.refresh(sub)

    return _to_response(sub)


def delete_subscription(db: Session, sub_id: int, user: User) -> None:
    sub = db.query(EmailSubscription).filter(EmailSubscription.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    if user.role.value != "manager" and sub.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another user's subscription")

    db.delete(sub)
    db.commit()


def get_subscribers_for_event(db: Session, event_type: str) -> list[str]:
    """Get list of emails that should be notified for a given event type."""
    query = db.query(EmailSubscription).filter(EmailSubscription.is_active == True)

    if event_type == "item_restocked":
        query = query.filter(EmailSubscription.notify_restock == True)
    elif event_type == "item_withdrawn":
        query = query.filter(EmailSubscription.notify_withdraw == True)
    elif event_type == "low_stock_alert":
        query = query.filter(EmailSubscription.notify_low_stock == True)
    else:
        return []

    subs = query.all()
    return list(set(s.email for s in subs))

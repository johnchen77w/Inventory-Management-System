from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.middleware.auth import require_manager

router = APIRouter()


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    if "role" in update_data:
        if update_data["role"] not in ["manager", "staff"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
        update_data["role"] = UserRole(update_data["role"])

    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

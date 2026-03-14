from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services import category_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return category_service.get_categories(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    cat = category_service.create_category(db, data)
    return {**cat.__dict__, "item_count": 0}


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    cat = category_service.update_category(db, category_id, data)
    return {**cat.__dict__, "item_count": 0}


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    category_service.delete_category(db, category_id)

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse, RestockRequest, WithdrawRequest
from app.services import item_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("", response_model=ItemListResponse)
def list_items(
    search: str | None = None,
    category_id: int | None = None,
    location_id: int | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
    below_threshold: bool = False,
    sort_by: str = Query("updated_at", pattern="^(name|sku|quantity|price|updated_at|created_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_manager),
):
    return item_service.list_items(
        db, search=search, category_id=category_id, location_id=location_id,
        min_quantity=min_quantity, max_quantity=max_quantity, below_threshold=below_threshold,
        sort_by=sort_by, order=order, page=page, per_page=per_page,
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return item_service.get_item(db, item_id)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return item_service.create_item(db, data, current_user)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, data: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    return item_service.update_item(db, item_id, data, current_user)


@router.patch("/{item_id}", response_model=ItemResponse)
def partial_update_item(item_id: int, data: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return item_service.update_item(db, item_id, data, current_user)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    item_service.delete_item(db, item_id, current_user)


@router.post("/{item_id}/restock", response_model=ItemResponse)
def restock_item(item_id: int, data: RestockRequest, db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return item_service.restock_item(db, item_id, data.quantity, data.notes, current_user)


@router.post("/{item_id}/withdraw", response_model=ItemResponse)
def withdraw_item(item_id: int, data: WithdrawRequest, db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return item_service.withdraw_item(db, item_id, data.quantity, data.notes, current_user)

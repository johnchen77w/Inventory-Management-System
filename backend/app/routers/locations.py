from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse
from app.services import location_service
from app.middleware.auth import require_manager, require_staff_or_manager

router = APIRouter()


@router.get("", response_model=list[LocationResponse])
def list_locations(db: Session = Depends(get_db), current_user: User = Depends(require_staff_or_manager)):
    return location_service.get_locations(db)


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(data: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    loc = location_service.create_location(db, data)
    return {**loc.__dict__, "item_count": 0}


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, data: LocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    loc = location_service.update_location(db, location_id, data)
    return {**loc.__dict__, "item_count": 0}


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    location_service.delete_location(db, location_id)

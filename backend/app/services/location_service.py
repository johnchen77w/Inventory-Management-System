from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from fastapi import HTTPException, status

from app.models.location import Location
from app.models.item import Item
from app.schemas.location import LocationCreate, LocationUpdate


def get_locations(db: Session) -> list[dict]:
    locations = db.query(Location).all()
    result = []
    for loc in locations:
        count = db.query(sa_func.count(Item.id)).filter(Item.location_id == loc.id).scalar()
        result.append({**loc.__dict__, "item_count": count})
    return result


def get_location(db: Session, location_id: int) -> Location:
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


def create_location(db: Session, data: LocationCreate) -> Location:
    existing = db.query(Location).filter(Location.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Location name already exists")
    location = Location(**data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def update_location(db: Session, location_id: int, data: LocationUpdate) -> Location:
    location = get_location(db, location_id)
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(Location).filter(Location.name == update_data["name"], Location.id != location_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Location name already exists")
    for key, value in update_data.items():
        setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location


def delete_location(db: Session, location_id: int) -> None:
    location = get_location(db, location_id)
    item_count = db.query(sa_func.count(Item.id)).filter(Item.location_id == location_id).scalar()
    if item_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot delete location with {item_count} items")
    db.delete(location)
    db.commit()

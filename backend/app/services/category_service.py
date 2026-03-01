from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from fastapi import HTTPException, status

from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories(db: Session) -> list[dict]:
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        count = db.query(sa_func.count(Item.id)).filter(Item.category_id == cat.id).scalar()
        result.append({**cat.__dict__, "item_count": count})
    return result


def get_category(db: Session, category_id: int) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id)
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(Category).filter(Category.name == update_data["name"], Category.id != category_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    item_count = db.query(sa_func.count(Item.id)).filter(Item.category_id == category_id).scalar()
    if item_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot delete category with {item_count} items")
    db.delete(category)
    db.commit()

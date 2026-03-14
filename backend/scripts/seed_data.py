"""Seed the database with sample data for development."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.category import Category
from app.models.location import Location
from app.models.item import Item


def seed():
    db = SessionLocal()
    try:
        # Categories
        categories = [
            Category(name="Electronics", description="Electronic components and devices"),
            Category(name="Raw Materials", description="Unprocessed materials for manufacturing"),
            Category(name="Office Supplies", description="General office supplies and stationery"),
            Category(name="Packaging", description="Packaging materials and containers"),
            Category(name="Tools", description="Hand tools and power tools"),
        ]
        for cat in categories:
            existing = db.query(Category).filter(Category.name == cat.name).first()
            if not existing:
                db.add(cat)
        db.commit()

        # Locations
        locations = [
            Location(name="Warehouse A", description="Main storage warehouse", address="100 Industrial Ave"),
            Location(name="Warehouse B", description="Secondary warehouse", address="200 Industrial Ave"),
            Location(name="Shelf B-3", description="Aisle B, Shelf 3", address="Warehouse A"),
            Location(name="Cold Storage", description="Temperature-controlled storage", address="150 Industrial Ave"),
        ]
        for loc in locations:
            existing = db.query(Location).filter(Location.name == loc.name).first()
            if not existing:
                db.add(loc)
        db.commit()

        # Get IDs
        electronics = db.query(Category).filter(Category.name == "Electronics").first()
        raw_materials = db.query(Category).filter(Category.name == "Raw Materials").first()
        office = db.query(Category).filter(Category.name == "Office Supplies").first()
        warehouse_a = db.query(Location).filter(Location.name == "Warehouse A").first()
        warehouse_b = db.query(Location).filter(Location.name == "Warehouse B").first()
        shelf_b3 = db.query(Location).filter(Location.name == "Shelf B-3").first()

        # Items
        items = [
            Item(sku="ELEC-001", name="Arduino Uno R3", description="Microcontroller board",
                 category_id=electronics.id, location_id=warehouse_a.id,
                 quantity=150, unit="pcs", price=25.99, low_stock_threshold=20),
            Item(sku="ELEC-002", name="Raspberry Pi 4B", description="Single-board computer 4GB RAM",
                 category_id=electronics.id, location_id=warehouse_a.id,
                 quantity=75, unit="pcs", price=55.00, low_stock_threshold=15),
            Item(sku="ELEC-003", name="USB-C Cable 1m", description="USB Type-C charging cable",
                 category_id=electronics.id, location_id=shelf_b3.id,
                 quantity=500, unit="pcs", price=3.99, low_stock_threshold=50),
            Item(sku="RAW-001", name="Copper Wire 14AWG", description="Solid copper wire, 100ft roll",
                 category_id=raw_materials.id, location_id=warehouse_b.id,
                 quantity=30, unit="rolls", price=45.50, low_stock_threshold=10),
            Item(sku="RAW-002", name="Aluminum Sheet 4x8", description="6061-T6 aluminum sheet",
                 category_id=raw_materials.id, location_id=warehouse_b.id,
                 quantity=8, unit="sheets", price=120.00, low_stock_threshold=5),
            Item(sku="OFF-001", name="A4 Paper Ream", description="80gsm white A4 paper, 500 sheets",
                 category_id=office.id, location_id=shelf_b3.id,
                 quantity=200, unit="reams", price=6.99, low_stock_threshold=25),
            Item(sku="OFF-002", name="Ballpoint Pen Pack", description="12-pack blue ballpoint pens",
                 category_id=office.id, location_id=shelf_b3.id,
                 quantity=5, unit="packs", price=4.50, low_stock_threshold=10),
        ]
        for item in items:
            existing = db.query(Item).filter(Item.sku == item.sku).first()
            if not existing:
                db.add(item)
        db.commit()

        print("Seed data created successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

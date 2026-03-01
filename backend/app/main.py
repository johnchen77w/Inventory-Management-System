from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.models.user import UserRole
from app.utils.security import hash_password
from app.routers import auth, users, categories, locations, items, logs, alerts, dashboard


def seed_admin():
    """Create default admin user if not exists."""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.default_admin_email).first()
        if not existing:
            admin = User(
                email=settings.default_admin_email,
                hashed_password=hash_password(settings.default_admin_password),
                full_name=settings.default_admin_name,
                role=UserRole.manager,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"Default admin created: {settings.default_admin_email}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed default admin (migrations handled by start.sh)
    seed_admin()
    yield
    # Shutdown


app = FastAPI(
    title="Inventory Management System",
    description="Cloud-native inventory management with real-time updates",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}

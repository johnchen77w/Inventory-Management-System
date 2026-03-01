"""Test fixtures for the Inventory Management System API."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.utils.security import hash_password, create_access_token

# Use SQLite in-memory for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Provide a test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def manager_user(db) -> User:
    """Create a manager user for testing."""
    user = User(
        email="manager@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Manager",
        role=UserRole.manager,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def staff_user(db) -> User:
    """Create a staff user for testing."""
    user = User(
        email="staff@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Staff",
        role=UserRole.staff,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def manager_token(manager_user) -> str:
    """Generate a JWT token for the manager user."""
    return create_access_token({"sub": str(manager_user.id)})


@pytest.fixture
def staff_token(staff_user) -> str:
    """Generate a JWT token for the staff user."""
    return create_access_token({"sub": str(staff_user.id)})


@pytest.fixture
def manager_headers(manager_token) -> dict:
    """Authorization headers for manager."""
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture
def staff_headers(staff_token) -> dict:
    """Authorization headers for staff."""
    return {"Authorization": f"Bearer {staff_token}"}

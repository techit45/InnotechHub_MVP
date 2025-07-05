"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Create test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database tables automatically"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Create test user
    client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    })
    
    # Login and get token
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "testpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def trainer_headers(client):
    """Get trainer authentication headers"""
    # Create trainer user
    client.post("/auth/register", json={
        "email": "trainer@example.com",
        "password": "trainerpass123",
        "first_name": "Trainer",
        "last_name": "User",
        "role": "trainer"
    })
    
    # Login and get token
    response = client.post("/auth/login", json={
        "email": "trainer@example.com",
        "password": "trainerpass123"
    })
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
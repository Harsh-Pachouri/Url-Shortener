# In conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from crud import Base, get_db

# Use PostgreSQL for testing in CI, SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # CI environment - use PostgreSQL
    engine = create_engine(DATABASE_URL)
else:
    # Local development - use SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the fixture that will be used by our tests
@pytest.fixture()
def client():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    
    # This function will override the main get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Yield the client for the test to use
    yield TestClient(app)
    
    # Drop all tables after tests are done to keep it clean
    Base.metadata.drop_all(bind=engine)
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.db.database import get_db, Base
from app.models.models import User, Ticker
import uuid

# Test database URL (use in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test user
    db = TestingSessionLocal()
    test_user = User(username="testuser", password_hash="hashedpassword")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create test ticker
    test_ticker = Ticker(symbol="AAPL", company_name="Apple Inc.", sector="Technology")
    db.add(test_ticker)
    db.commit()
    db.refresh(test_ticker)
    
    yield {"user_id": str(test_user.user_id), "ticker_id": str(test_ticker.ticker_id)}
    
    # Clean up
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_portfolio(setup_database):
    user_id = setup_database["user_id"]
    
    portfolio_data = {
        "name": "Test Portfolio",
        "base_currency": "USD",
        "created_by": str(user_id)
    }
    
    response = client.post("/api/v1/portfolios/", json=portfolio_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Portfolio"
    assert data["base_currency"] == "USD"
    assert data["created_by"] == str(user_id)


def test_get_portfolios(setup_database):
    user_id = setup_database["user_id"]
    
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio",
        "base_currency": "USD",
        "created_by": str(user_id)
    }
    client.post("/api/v1/portfolios/", json=portfolio_data)
    
    # Then get portfolios
    response = client.get(f"/api/v1/portfolios/?user_id={user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Portfolio"


def test_add_stock_to_portfolio(setup_database):
    user_id = setup_database["user_id"]
    ticker_id = setup_database["ticker_id"]
    
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio",
        "base_currency": "USD",
        "created_by": str(user_id)
    }
    portfolio_response = client.post("/api/v1/portfolios/", json=portfolio_data)
    portfolio_id = portfolio_response.json()["portfolio_id"]
    
    # Add stock to portfolio
    stock_data = {
        "ticker_id": str(ticker_id),
        "quantity": 10.0,
        "market_value": 1500.0
    }
    
    response = client.post(f"/api/v1/portfolios/{portfolio_id}/stocks?user_id={user_id}", json=stock_data)
    assert response.status_code == 201
    
    data = response.json()
    assert float(data["quantity"]) == 10.0
    assert float(data["market_value"]) == 1500.0


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

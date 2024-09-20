from fastapi.testclient import TestClient
from main import app
from database import get_db
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import pytest

import json

client = TestClient(app)

# Create a mock database session
def mock_get_db():
    db = MagicMock()
    # Mock a user object that would come from the database
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.password = "testpassword"  # Assuming passwords are not hashed in this simple test
    db.query().filter().first.return_value = mock_user
    yield db

# Test that protected route returns 401 Unauthorized when no token is provided
def test_protected_route_without_token():
    response = client.get("/protected/")
    assert response.status_code == 401

# Override the get_db dependency in your app
@pytest.fixture(autouse=True)
def override_get_db():
    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides[get_db] = None

# Example test case for login
def test_login():
    # Send correct login data (as per your Pydantic LoginRequest model)
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # Send POST request to login endpoint
    response = client.post("/login/", json=login_data)

    # Assert that the login is successful (status code 200)
    assert response.status_code == 200
    assert "access_token" in response.json()

# Example test case for a protected route using a mock token
def test_protected_route():
    # Mock token and headers
    headers = {
        "Authorization": "Bearer mocked_token"
    }

    response = client.get("/protected/", headers=headers)

    assert response.status_code == 200
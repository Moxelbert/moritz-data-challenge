from fastapi.testclient import TestClient
from main import app, get_current_user, create_access_token, verify_access_token
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

# Mocked version of create_access_token
def mock_create_access_token(data: dict):
    return "mocked_token"

# Mocked version of verify_access_token
def mock_verify_access_token(token: str):
    if token == "mocked_token":
        return {"sub": "testuser"}  # Mock payload with user info
    else:
        return None  # Return None for invalid token

# Override dependencies for the tests
@pytest.fixture(autouse=True)
def override_dependencies():
    # Patch verify_access_token
    app.dependency_overrides[verify_access_token] = mock_verify_access_token
    yield
    app.dependency_overrides = {}

# Test the login route (mocking create_access_token)
@patch("main.create_access_token", mock_create_access_token)  # Use patch to mock create_access_token
def test_login():
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # Simulate a login request
    response = client.post("/login/", json=login_data)

    # Assert that the login was successful
    assert response.status_code == 200
    # Assert that the token returned is the mocked token
    assert response.json()["access_token"] == "mocked_token"

# Test case for invalid file upload
def test_invalid_file_upload():
    # This JSON data doesn't match the expected Pydantic model
    invalid_json_content = {
        "invalid_key": "2024-09-15T12:00:00Z",  # Missing 'timestamp' and 'data'
        "data": "not an array of floats"        # 'data' should be an array of floats
    }

    # Simulate a POST request to upload the invalid JSON
    response = client.post(
        "/upload-json",  # Adjust this to your actual upload endpoint
        files={"file": ("invalid.json", json.dumps(invalid_json_content), "application/json")}
    )

    # Assert that the response status code is 422 (Unprocessable Entity)
    assert response.status_code == 422
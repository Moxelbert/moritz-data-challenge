from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
import pytest

import json

client = TestClient(app)

# Test that protected route returns 401 Unauthorized when no token is provided
def test_protected_route_without_token():
    response = client.get("/protected/")
    assert response.status_code == 401

# Mock the dependency to simulate an authenticated user
def mock_get_current_user():
    return {"username": "user1"}

# Test that the protected route is accessible with valid authentication
@patch("main.get_current_user", mock_get_current_user)  # Patch the actual function used in the app
def test_protected_route_with_token():
    response = client.get("/protected/")
    assert response.status_code == 200
    assert response.json() == {"message": "You are authorized", "user": "testuser"}

# Test invalid JSON upload
@patch("main.get_current_user", mock_get_current_user)  # Mock the user for this test as well
def test_upload_invalid_json():
    invalid_json_content = {
        "invalid_key": "2024-09-15T12:00:00Z",
        "data": "not an array of floats"
    }

    response = client.post(
        "/upload-json",  # Add the leading slash
        files={"file": ("invalid.json", json.dumps(invalid_json_content), "application/json")}
    )

    # Assert that the response status code is 422 (or change based on your validation logic)
    assert response.status_code == 422
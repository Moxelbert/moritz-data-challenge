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

# Test the full authentication flow (login and access protected route)
def test_protected_route_with_token():
    # Simulate a login request to get a real token
    response = client.post("/login", data={"username": "user1", "password": "123password"})
    
    # Extract the token from the login response
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Pass the token in the Authorization header
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Access the protected route with the valid token
    response = client.get("/protected/", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"message": "You are authorized", "user": "user1"}

# Test invalid JSON upload
def test_upload_invalid_json():
    # Simulate a login request to get a real token
    response = client.post("/login", data={"username": "user1", "password": "123password"})
    
    # Extract the token from the login response
    token = response.json()["access_token"]

    # Create invalid JSON content
    invalid_json_content = {
        "invalid_key": "2024-09-15T12:00:00Z",
        "data": "not an array of floats"
    }

    # Pass the token in the Authorization header
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send the invalid JSON file
    response = client.post(
        "/upload-json",
        files={"file": ("invalid.json", json.dumps(invalid_json_content), "application/json")},
        headers=headers
    )

    # Assert that the response status code is 422
    assert response.status_code == 422
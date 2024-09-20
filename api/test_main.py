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

# Test case for the full authentication process
def test_full_authentication_process():
    # Step 1: Simulate a login request
    login_data = {
        "username": "user1",   # Make sure this user exists in your database
        "password": "123password"  # Correct password for the user
    }

    # Send a POST request to the login endpoint
    response = client.post("/login/", json=login_data)

    # Ensure the login was successful (status code 200)
    assert response.status_code == 200

    # Extract the token from the response
    token_data = response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # Step 2: Use the returned token to access a protected rout
    headers = {
        "Authorization": f"Bearer {access_token}"  # Pass the JWT token in the Authorization header
    }

    # Send a GET request to a protected route (replace with your actual protected route)
    protected_response = client.get("/protected/", headers=headers)

    # Ensure the protected route is accessible with the valid token
    assert protected_response.status_code == 200
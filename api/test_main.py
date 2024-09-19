from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

# Test that protected route returns 401 Unauthorized when no token is provided
def test_protected_route_without_token():
    response = client.get("/protected/")
    assert response.status_code == 401
    #assert response.json() == {"detail": "Not authenticated"}
'''
# Mock the dependency to simulate an authenticated user
def mock_get_current_user():
    return {"username": "testuser"}

# Test that the protected route is accessible with valid authentication
@patch("main.get_current_user", mock_get_current_user)  # Mock the user authentication
def test_protected_route_with_token():
    response = client.get("/protected/")
    assert response.status_code == 200
    #assert response.json() == {"message": "You are authorized", "user": "testuser"}
'''
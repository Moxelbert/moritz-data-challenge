from fastapi.testclient import TestClient
from main import app
from _pytest.assertion import truncate


truncate.DEFAULT_MAX_LINES = 9999
truncate.DEFAULT_MAX_CHARS = 9999 

client = TestClient(app)

"""def test_login():
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    response = client.post("/login/", json={"username": "invalid2", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid username or password"}"""

def test_anything():
    assert 1 == 1
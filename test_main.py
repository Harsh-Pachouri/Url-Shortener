import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient # Import TestClient here


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Welcome!": "This is a URL shortener"}

def test_create_user(client: TestClient):
    new_user_data = {
        "username": "testuser_from_test",
        "password": "testpassword"
    }
    response = client.post("/register", json=new_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser_from_test"
    assert "id" in data

def test_create_user_duplicate_username(client: TestClient):
    user_data = {
        "username": "test_duplicate",
        "password": "testpassword"
    }
    response1 = client.post("/register", json=user_data)
    assert response1.status_code == 200

    response2 = client.post("/register", json=user_data)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Username already taken"
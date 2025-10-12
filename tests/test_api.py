import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the POS system!"}

def test_create_pos_item():
    response = client.post("/pos/", json={"name": "Item1", "price": 100})
    assert response.status_code == 201
    assert response.json()["name"] == "Item1"

def test_read_pos_item():
    response = client.get("/pos/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_pos_item():
    response = client.put("/pos/1", json={"name": "Updated Item", "price": 150})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Item"

def test_delete_pos_item():
    response = client.delete("/pos/1")
    assert response.status_code == 204
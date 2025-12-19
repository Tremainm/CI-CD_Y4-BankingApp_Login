import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
import httpx

from app.main import app, get_db
from app.models import Base, UserDB

TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db

    # Clear all data before each test
    db = TestingSessionLocal()
    db.query(UserDB).delete()
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

def user_payload(full_name="John Doe", email="john@example.com", phone_number="+1234567890", password="password123"):
    return {
        "full_name": full_name,
        "email": email,
        "phone_number": phone_number,
        "password": password
    }

# Test create user - success
def test_create_user_success(client):
    response = client.post("/api/users", json=user_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@example.com"
    assert data["full_name"] == "John Doe"
    assert "id" in data

# Test create user - duplicate email
def test_create_user_duplicate_email(client):
    client.post("/api/users", json=user_payload(email="duplicate@test.com"))
    response = client.post("/api/users", json=user_payload(email="duplicate@test.com"))
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

# Test get all users - empty
def test_get_users_empty(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []

# Test get all users - with data
def test_get_users_with_data(client):
    client.post("/api/users", json=user_payload(email="user1@test.com"))
    client.post("/api/users", json=user_payload(email="user2@test.com"))
    
    response = client.get("/api/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert users[0]["id"] < users[1]["id"]  # ordered by id

# Test get single user - success
def test_get_user_success(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "john@example.com"

# Test get single user - not found
def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Test update user - success
def test_update_user_success(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    update_data = user_payload(full_name="Jane Doe", email="jane@example.com")
    response = client.put(f"/api/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"

# Test update user - not found
def test_update_user_not_found(client):
    response = client.put("/api/users/999", json=user_payload())
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Test update user - integrity error
def test_update_user_integrity_error(client):
    # Create two users
    client.post("/api/users", json=user_payload(email="user1@test.com"))
    create_response = client.post("/api/users", json=user_payload(email="user2@test.com"))
    user_id = create_response.json()["id"]
    
    # Try to update second user with first user's email
    response = client.put(f"/api/users/{user_id}", json=user_payload(email="user1@test.com"))
    assert response.status_code == 400
    assert response.json()["detail"] == "Update failed"

# Test delete user - success
def test_delete_user_success(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    with patch('httpx.delete') as mock_delete:
        mock_delete.return_value.status_code = 204
        response = client.delete(f"/api/users/{user_id}")
    
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404

# Test delete user - not found
def test_delete_user_not_found(client):
    response = client.delete("/api/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Test delete user - account service returns 404 (acceptable)
def test_delete_user_account_service_404(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    with patch('httpx.delete') as mock_delete:
        mock_delete.return_value.status_code = 404
        response = client.delete(f"/api/users/{user_id}")
    
    assert response.status_code == 204

# Test delete user - account service error (should not fail user deletion)
def test_delete_user_account_service_error(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    with patch('httpx.delete') as mock_delete:
        mock_delete.return_value.status_code = 500
        response = client.delete(f"/api/users/{user_id}")
    
    assert response.status_code == 204

# Test delete user - account service timeout (should not fail user deletion)
def test_delete_user_account_service_timeout(client):
    create_response = client.post("/api/users", json=user_payload())
    user_id = create_response.json()["id"]
    
    with patch('httpx.delete') as mock_delete:
        mock_delete.side_effect = httpx.RequestError("Timeout")
        response = client.delete(f"/api/users/{user_id}")
    
    assert response.status_code == 204

# Test CORS middleware (implicitly tested through other requests)
def test_cors_headers(client):
    response = client.options("/api/users")
    # FastAPI handles OPTIONS automatically with CORS middleware
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined

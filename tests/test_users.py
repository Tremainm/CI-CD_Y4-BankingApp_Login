import pytest
from app.main import users 

def setup_function():
    users.clear()

def user_payload(uid=1, full_name="Paul Doe", email="pl@atu.ie", phone="+1234567890", password="password123"):
    return {
        "id": uid,
        "full_name": full_name,
        "email": email,
        "phone_number": phone,
        "password": password
    }

def test_register_user_ok(client):
    r = client.post("/user/register/", json=user_payload())
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "pl@atu.ie"

def test_duplicate_email_400(client):
    client.post("/user/register/", json=user_payload(email="dup@atu.ie"))
    r = client.post("/user/register/", json=user_payload(email="dup@atu.ie"))
    assert r.status_code == 400
    assert "Email" in r.json()["detail"]

def test_get_user_404(client):
    r = client.get("/user/get_user/999")
    assert r.status_code == 404

def test_update_user_ok(client):
    client.post("/user/register/", json=user_payload(uid=1))
    r = client.put("/user/update/1", json=user_payload(uid=1, full_name="Anesu"))
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["full_name"] == "Anesu"

def test_delete_user_ok(client):
    client.post("/user/register/", json=user_payload(uid=2))
    r = client.delete("/user/delete_user/2")
    assert r.status_code == 200
    assert "deleted" in r.json()["message"].lower()

def test_update_password_ok(client):
    client.post("/user/register/", json=user_payload(uid=3))
    r = client.put("/user/update_password/3", params={"new_password": "newpass"})
    assert r.status_code == 200
    assert "Password" in r.json()["message"]

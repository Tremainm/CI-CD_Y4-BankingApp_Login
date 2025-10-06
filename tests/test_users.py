import pytest

# Creating a testing dict
def user_payload(uname="johndoe", email="johndoe@atu.ie", phoneNo="012345678", passw="password"):
    return {"username": uname, "email": email, "phone_number": phoneNo, "password": passw}

# Test user creation success. checks all data in test dict
def test_create_user_ok(client):
    r = client.post("/users", json=user_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "johndoe"
    assert data["email"] == "johndoe@atu.ie"
    assert data["phone_number"] == "012345678"
    assert data["password"] == "password"

# Checks if duplicate email exists
def test_duplicate_email_conflict(client):
    client.post("/users", json=user_payload(email="tremain@atu.ie"))
    r = client.post("/users", json=user_payload(email="tremain@atu.ie"))
    assert r.status_code == 409 # duplicate id -> conflict
    assert "exists" in r.json()["detail"].lower()

# Checks if duplicate phone number exists
def test_duplicate_phoneNo_conflict(client):
    client.post("/users", json=user_payload(phoneNo="123456789"))
    r = client.post("/users", json=user_payload(phoneNo="123456789"))
    assert r.status_code == 409 # duplicate id -> conflict
    assert "exists" in r.json()["detail"].lower()

# check if 'bad' phone numbers fail correctly
@pytest.mark.parametrize("bad_phoneNo", ["012345", "a12345678", "1234567890", "a2345g"]) # one test can try multiple invalid inputs
def test_bad_student_id_422(client, bad_phoneNo):
    r = client.post("/users", json=user_payload(email="tom@atu.ie", phoneNo=bad_phoneNo))
    assert r.status_code == 422 # pydantic validation error

# if user doesn't exist, get 404
def test_get_user_404(client):
    r = client.get("/users/jane@atu.ie")
    assert r.status_code == 404

# if deleted successfully, return 204, if user not found, return 404
def test_delete_then_404(client):
    r1 = client.delete("/users/johndoe@atu.ie")
    assert r1.status_code == 204
    r2 = client.delete("/users/johndoe@atu.ie")
    assert r2.status_code == 404

# test to check if user update is successful
def test_update_user_ok(client):
    client.post("/users", json=user_payload(email="tman@atu.ie"))
    r = client.put("/users/tman@atu.ie", json=user_payload(email="tman@atu.ie", uname="Tremain")) # update username to 'Tremain'
    assert r.status_code == 200
    data = r.json() # 'Tremain' parsed as json & stored in 'data'
    assert data["username"] == "Tremain" # check if name was updated
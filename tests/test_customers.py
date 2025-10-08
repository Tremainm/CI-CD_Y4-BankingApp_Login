import pytest

# Helper function to build a reusable customer payload
def customer_payload(
    cid=1,
    name="Paul",
    full_name="Paul Murphy",
    email="paul.murphy@example.com",
    age=25,
    password="Str0ngPass1"
):
    return {
        "customer_id": cid,
        "name": name,
        "full_name": full_name,
        "email": email,
        "age": age,
        "password": password
    }

#Get customers
def test_list_customers_returns_all(client):
    """Test that GET /api/customers returns all created customers"""
    # Clear old data and create two customers (so the list isn't empty)
    client.post("/api/customers", json={
        "customer_id": 100,
        "name": "Alice",
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 30,
        "password": "Pass1234"
    })
    client.post("/api/customers", json={
        "customer_id": 101,
        "name": "Bob",
        "full_name": "Bob Smith",
        "email": "bob@example.com",
        "age": 35,
        "password": "Strong123"
    })

    # Call the list endpoint
    r = client.get("/api/customers")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, list) # response should be a list
    assert len(data) >= 2  # At least the two that were created

   # Check that expected keys exist for each item
    assert "customer_id" in data[0]
    assert "email" in data[0]
    assert "password" in data[0]  


# CREATE CUSTOMER 

def test_create_customer_ok(client):
    """Create a new customer successfully"""
    r = client.post("/api/customers", json=customer_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["customer_id"] == 1
    assert data["name"] == "Paul"
    assert data["full_name"] == "Paul Murphy"
    assert data["email"] == "paul.murphy@example.com"


def test_duplicate_customer_id_conflict(client):
    """Creating a customer with an existing ID should fail"""
    client.post("/api/customers", json=customer_payload(cid=2, email="unique1@example.com"))
    r = client.post("/api/customers", json=customer_payload(cid=2, email="unique2@example.com"))
    assert r.status_code == 409
    assert "exists" in r.json()["detail"].lower()


def test_duplicate_customer_email_conflict(client):
    """Creating a customer with an existing email should fail"""
    client.post("/api/customers", json=customer_payload(cid=3, email="dup@example.com"))
    r = client.post("/api/customers", json=customer_payload(cid=4, email="dup@example.com"))
    assert r.status_code == 409
    assert "registered" in r.json()["detail"].lower()


# GET CUSTOMER 

def test_get_customer_ok(client):
    """Retrieve an existing customer"""
    client.post("/api/customers", json=customer_payload(cid=5, email="p5@example.com"))
    r = client.get("/api/customers/5")
    assert r.status_code == 200
    data = r.json()
    assert data["customer_id"] == 5
    assert data["full_name"] == "Paul Murphy"


def test_get_customer_404(client):
    """Requesting a non-existent customer should return 404"""
    r = client.get("/api/customers/999")
    assert r.status_code == 404


#  VALIDATION TESTS 

@pytest.mark.parametrize("bad_email", ["name@", "name@.com", "name", "name.com", "name@domain"])
def test_invalid_email_422(client, bad_email):
    """Email must be a valid format"""
    r = client.post("/api/customers", json=customer_payload(cid=6, email=bad_email))
    assert r.status_code == 422


@pytest.mark.parametrize("bad_password", ["short7", "12345678", "allletters"])
def test_invalid_password_length_or_content(client, bad_password):
    """Password must have at least 8 chars (letters allowed, but length matters)"""
    r = client.post("/api/customers", json=customer_payload(cid=7, email="p7@example.com", password=bad_password))
    assert r.status_code == 422


@pytest.mark.parametrize("bad_age", [18, -1, 0])
def test_invalid_age_422(client, bad_age):
    """Age must be greater than 18"""
    r = client.post("/api/customers", json=customer_payload(cid=8, email="p8@example.com", age=bad_age))
    assert r.status_code == 422


# UPDATE CUSTOMER 

def test_update_customer_ok(client):
    """Update an existing customer's info"""
    client.post("/api/customers", json=customer_payload(cid=9, email="update@example.com"))
    updated = customer_payload(cid=999, name="Updated Name", full_name="Updated Customer", email="newemail@example.com")
    r = client.put("/api/customers/9", json=updated)
    assert r.status_code == 202
    data = r.json()
    assert data["customer_id"] == 9
    assert data["name"] == "Updated Name"
    assert data["email"] == "newemail@example.com"


def test_update_customer_404(client):
    """Updating a non-existent customer should fail"""
    updated = customer_payload(cid=10, email="noone@example.com")
    r = client.put("/api/customers/404404", json=updated)
    assert r.status_code == 404


# DELETE CUSTOMER 

def test_delete_customer_then_404(client):
    """Delete a customer, then confirm deletion"""
    client.post("/api/customers", json=customer_payload(cid=11, email="delete@example.com"))
    r1 = client.delete("/api/customers/11")
    assert r1.status_code == 204  # deleted successfully
    r2 = client.delete("/api/customers/11")
    assert r2.status_code == 404  # already deleted




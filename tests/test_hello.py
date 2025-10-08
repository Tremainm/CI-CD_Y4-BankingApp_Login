def test_hello(client):
    r = client.get("/hello")
    assert r.status_code == 200
    assert r.json() == {"message": "Customer Login service running"}
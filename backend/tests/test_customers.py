def test_create_customer(client):
    response = client.post("/api/v1/customers", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+1555123456",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_create_customer_duplicate_email(client):
    client.post("/api/v1/customers", json={
        "full_name": "John", "email": "dup@example.com",
    })
    response = client.post("/api/v1/customers", json={
        "full_name": "Jane", "email": "dup@example.com",
    })
    assert response.status_code == 409


def test_create_customer_duplicate_phone(client):
    client.post("/api/v1/customers", json={
        "full_name": "Alice", "email": "alice@example.com", "phone_number": "+1555000000",
    })
    response = client.post("/api/v1/customers", json={
        "full_name": "Bob", "email": "bob@example.com", "phone_number": "+1555000000",
    })
    assert response.status_code == 409


def test_create_customer_invalid_email(client):
    response = client.post("/api/v1/customers", json={
        "full_name": "John", "email": "not-an-email",
    })
    assert response.status_code == 422


def test_get_customer(client):
    create_resp = client.post("/api/v1/customers", json={
        "full_name": "Jane", "email": "jane@example.com",
    })
    cid = create_resp.json()["id"]
    response = client.get(f"/api/v1/customers/{cid}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane"


def test_get_customer_not_found(client):
    response = client.get("/api/v1/customers/99999")
    assert response.status_code == 404


def test_list_customers(client):
    client.post("/api/v1/customers", json={
        "full_name": "A", "email": "a@example.com",
    })
    client.post("/api/v1/customers", json={
        "full_name": "B", "email": "b@example.com",
    })
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_delete_customer(client):
    create_resp = client.post("/api/v1/customers", json={
        "full_name": "To Delete", "email": "delete@example.com",
    })
    cid = create_resp.json()["id"]
    response = client.delete(f"/api/v1/customers/{cid}")
    assert response.status_code == 200
    get_resp = client.get(f"/api/v1/customers/{cid}")
    assert get_resp.status_code == 404

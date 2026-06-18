def test_create_product(client):
    response = client.post("/api/v1/products", json={
        "product_name": "Test Product",
        "sku": "TP-001",
        "price": 19.99,
        "quantity_in_stock": 50,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["product_name"] == "Test Product"
    assert data["sku"] == "TP-001"
    assert float(data["price"]) == 19.99
    assert data["quantity_in_stock"] == 50
    assert "id" in data


def test_create_product_duplicate_sku(client):
    client.post("/api/v1/products", json={
        "product_name": "Product A",
        "sku": "SKU-001",
        "price": 10.0,
        "quantity_in_stock": 10,
    })
    response = client.post("/api/v1/products", json={
        "product_name": "Product B",
        "sku": "SKU-001",
        "price": 20.0,
        "quantity_in_stock": 20,
    })
    assert response.status_code == 409


def test_create_product_invalid_price(client):
    response = client.post("/api/v1/products", json={
        "product_name": "Test",
        "sku": "TST",
        "price": -5,
        "quantity_in_stock": 10,
    })
    assert response.status_code == 422


def test_create_product_negative_quantity(client):
    response = client.post("/api/v1/products", json={
        "product_name": "Test",
        "sku": "TST",
        "price": 10,
        "quantity_in_stock": -5,
    })
    assert response.status_code == 422


def test_get_product(client):
    create_resp = client.post("/api/v1/products", json={
        "product_name": "Test",
        "sku": "GET-TEST",
        "price": 15.0,
        "quantity_in_stock": 30,
    })
    pid = create_resp.json()["id"]
    response = client.get(f"/api/v1/products/{pid}")
    assert response.status_code == 200
    assert response.json()["product_name"] == "Test"


def test_get_product_not_found(client):
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404


def test_list_products(client):
    client.post("/api/v1/products", json={
        "product_name": "P1", "sku": "P1-SKU", "price": 10, "quantity_in_stock": 5,
    })
    client.post("/api/v1/products", json={
        "product_name": "P2", "sku": "P2-SKU", "price": 20, "quantity_in_stock": 15,
    })
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_products_with_search(client):
    client.post("/api/v1/products", json={
        "product_name": "Wireless Mouse", "sku": "WM-001", "price": 29.99, "quantity_in_stock": 10,
    })
    client.post("/api/v1/products", json={
        "product_name": "Keyboard", "sku": "KB-001", "price": 49.99, "quantity_in_stock": 20,
    })
    response = client.get("/api/v1/products?search=Mouse")
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_update_product(client):
    create_resp = client.post("/api/v1/products", json={
        "product_name": "Original", "sku": "ORIG", "price": 10, "quantity_in_stock": 5,
    })
    pid = create_resp.json()["id"]
    response = client.put(f"/api/v1/products/{pid}", json={"product_name": "Updated"})
    assert response.status_code == 200
    assert response.json()["product_name"] == "Updated"


def test_delete_product(client):
    create_resp = client.post("/api/v1/products", json={
        "product_name": "To Delete", "sku": "DEL", "price": 5, "quantity_in_stock": 1,
    })
    pid = create_resp.json()["id"]
    response = client.delete(f"/api/v1/products/{pid}")
    assert response.status_code == 200
    get_resp = client.get(f"/api/v1/products/{pid}")
    assert get_resp.status_code == 404


def test_low_stock_products(client):
    client.post("/api/v1/products", json={
        "product_name": "Low Stock", "sku": "LOW", "price": 5, "quantity_in_stock": 3,
    })
    response = client.get("/api/v1/products/low-stock?threshold=10")
    assert response.status_code == 200
    assert len(response.json()) == 1

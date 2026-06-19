def test_create_order(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "Widget", "sku": "WDG001", "price": 25.0, "quantity_in_stock": 100,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Order Tester", "email": "order@example.com",
    })
    response = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 3}],
    })
    assert response.status_code == 201
    data = response.json()
    assert float(data["total_amount"]) == 75.0
    assert data["status"] == "pending"
    assert len(data["items"]) == 1


def test_create_order_customer_not_found(client):
    response = client.post("/api/v1/orders", json={
        "customer_id": 99999,
        "items": [{"product_id": 1, "quantity": 1}],
    })
    assert response.status_code == 404


def test_create_order_product_not_found(client):
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Test", "email": "test@example.com",
    })
    response = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": 99999, "quantity": 1}],
    })
    assert response.status_code == 404


def test_create_order_insufficient_stock(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "Limited", "sku": "LIM001", "price": 10, "quantity_in_stock": 2,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Stock Tester", "email": "stock@example.com",
    })
    response = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 5}],
    })
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_create_order_reduces_inventory(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "Deduct", "sku": "DED001", "price": 10, "quantity_in_stock": 50,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Deduct Tester", "email": "deduct@example.com",
    })
    client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 10}],
    })
    prod_get = client.get(f"/api/v1/products/{prod_resp.json()['id']}")
    assert prod_get.json()["quantity_in_stock"] == 40


def test_get_order(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "GetTest", "sku": "GETORD", "price": 15, "quantity_in_stock": 20,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Get Tester", "email": "gett@example.com",
    })
    order_resp = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 2}],
    })
    oid = order_resp.json()["id"]
    response = client.get(f"/api/v1/orders/{oid}")
    assert response.status_code == 200
    assert response.json()["id"] == oid


def test_get_order_not_found(client):
    response = client.get("/api/v1/orders/99999")
    assert response.status_code == 404


def test_list_orders(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "ListTest", "sku": "LSTORD", "price": 5, "quantity_in_stock": 30,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "List Tester", "email": "listt@example.com",
    })
    client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 1}],
    })
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_delete_order(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "DelTest", "sku": "DELORD", "price": 8, "quantity_in_stock": 10,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Del Tester", "email": "delt@example.com",
    })
    order_resp = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 1}],
    })
    oid = order_resp.json()["id"]
    response = client.delete(f"/api/v1/orders/{oid}")
    assert response.status_code == 200
    get_resp = client.get(f"/api/v1/orders/{oid}")
    assert get_resp.status_code == 404


def test_update_order_status_to_delivered(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "DeliverTest", "sku": "DELIVER01", "price": 10, "quantity_in_stock": 20,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Deliver Tester", "email": "deliver@example.com",
    })
    order_resp = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 5}],
    })
    oid = order_resp.json()["id"]
    response = client.patch(f"/api/v1/orders/{oid}/status", json={"status": "delivered"})
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"


def test_update_order_status_to_cancelled_restores_stock(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "CancelTest", "sku": "CANCEL01", "price": 10, "quantity_in_stock": 30,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Cancel Tester", "email": "cancel@example.com",
    })
    order_resp = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 10}],
    })
    oid = order_resp.json()["id"]
    response = client.patch(f"/api/v1/orders/{oid}/status", json={"status": "cancelled"})
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    prod_get = client.get(f"/api/v1/products/{prod_resp.json()['id']}")
    assert prod_get.json()["quantity_in_stock"] == 30


def test_cannot_revert_status(client):
    prod_resp = client.post("/api/v1/products", json={
        "product_name": "RevertTest", "sku": "REVERT01", "price": 10, "quantity_in_stock": 10,
    })
    cust_resp = client.post("/api/v1/customers", json={
        "full_name": "Revert Tester", "email": "revert@example.com",
    })
    order_resp = client.post("/api/v1/orders", json={
        "customer_id": cust_resp.json()["id"],
        "items": [{"product_id": prod_resp.json()["id"], "quantity": 2}],
    })
    oid = order_resp.json()["id"]
    client.patch(f"/api/v1/orders/{oid}/status", json={"status": "delivered"})
    response = client.patch(f"/api/v1/orders/{oid}/status", json={"status": "cancelled"})
    assert response.status_code == 400


def test_update_order_status_not_found(client):
    response = client.patch("/api/v1/orders/99999/status", json={"status": "delivered"})
    assert response.status_code == 404


def test_update_order_status_invalid_value(client):
    response = client.patch("/api/v1/orders/1/status", json={"status": "invalid"})
    assert response.status_code == 422

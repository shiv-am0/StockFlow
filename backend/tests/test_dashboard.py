def test_dashboard_stats(client):
    client.post("/api/v1/products", json={
        "product_name": "DashProd", "sku": "DASH-001", "price": 10, "quantity_in_stock": 5,
    })
    client.post("/api/v1/customers", json={
        "full_name": "Dash Cust", "email": "dash@example.com",
    })
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "total_customers" in data
    assert "total_orders" in data
    assert "low_stock_count" in data

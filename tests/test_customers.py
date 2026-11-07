def test_customers_default_pagination(client, seed):
    response = client.get("/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(seed["customers"])
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 20
    assert data["items"][0]["id"] == 1


def test_customers_invalid_paging(client):
    for params in [{"page_size": 101}, {"page_size": 0}, {"page": 0}]:
        response = client.get("/customers", params=params)
        assert response.status_code == 422


def test_customers_city_filter(client, seed):
    city = seed["customers"][0]["city"]
    response = client.get("/customers", params={"city": city})
    assert response.status_code == 200
    expected = sum(1 for customer in seed["customers"] if customer["city"] == city)
    assert response.json()["total"] == expected


def test_get_customer_by_id(client, seed):
    customer_id = 1
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id
    assert response.json()["email"] == seed["customers"][0]["email"]


def test_unknown_customer(client):
    response = client.get("/customers/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_customer_orders_are_newest_first(client, seed):
    customer_id = 1
    response = client.get(f"/customers/{customer_id}/orders")
    assert response.status_code == 200
    orders = response.json()
    customer_orders = [
        order for order in seed["orders"] if order["customer_id"] == customer_id
    ]
    customer_orders.sort(key=lambda item: item["created_at"], reverse=True)
    assert len(orders) == len(customer_orders)
    assert orders[0]["id"] == customer_orders[0]["id"]


def test_unknown_customer_orders(client):
    response = client.get("/customers/99999/orders")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

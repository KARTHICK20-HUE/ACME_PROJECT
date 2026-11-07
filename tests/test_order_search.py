def test_search_orders_without_filters(client, seed):
    response = client.get("/orders/search")
    assert response.status_code == 200
    assert response.json()["total"] == len(seed["orders"])


def test_search_orders_by_status(client, seed):
    status = "placed"
    response = client.get("/orders/search", params={"status": status})
    assert response.status_code == 200
    expected = sum(1 for order in seed["orders"] if order["status"] == status)
    assert response.json()["total"] == expected


def test_search_orders_by_customer_id(client, seed):
    customer_id = 12
    response = client.get("/orders/search", params={"customer_id": customer_id})
    assert response.status_code == 200
    expected = sum(1 for order in seed["orders"] if order["customer_id"] == customer_id)
    assert response.json()["total"] == expected


def test_search_orders_by_date_range(client, seed):
    response = client.get(
        "/orders/search", params={"date_from": "2026-03-01", "date_to": "2026-03-31"}
    )
    assert response.status_code == 200
    expected = sum(
        1
        for order in seed["orders"]
        if "2026-03-01" <= order["created_at"][:10] <= "2026-03-31"
    )
    assert response.json()["total"] == expected


def test_search_orders_combined_filters(client, seed):
    response = client.get(
        "/orders/search",
        params={
            "status": "refunded",
            "customer_id": 12,
            "date_from": "2026-03-01",
            "date_to": "2026-03-31",
        },
    )
    assert response.status_code == 200
    expected = sum(
        1
        for order in seed["orders"]
        if order["status"] == "refunded"
        and order["customer_id"] == 12
        and "2026-03-01" <= order["created_at"][:10] <= "2026-03-31"
    )
    assert response.json()["total"] == expected


def test_search_orders_invalid_date_range(client):
    response = client.get(
        "/orders/search", params={"date_from": "2026-03-31", "date_to": "2026-03-01"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "date_from must be on or before date_to"


def test_search_orders_invalid_status(client):
    response = client.get("/orders/search", params={"status": "bogus"})
    assert response.status_code == 422


def test_search_orders_malformed_date(client):
    response = client.get("/orders/search", params={"date_from": "bad-date"})
    assert response.status_code == 422


def test_search_orders_result_ordering_and_last_page(client, seed):
    response = client.get("/orders/search", params={"page": 51, "page_size": 20})
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 51
    assert payload["items"] == []
    assert payload["total"] == len(seed["orders"])


def test_get_order_by_id_still_works(client):
    response = client.get("/orders/A-1001")
    assert response.status_code == 200
    assert response.json()["id"] == "A-1001"

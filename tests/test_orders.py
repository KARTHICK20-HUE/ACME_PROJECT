def test_orders_are_paginated_and_newest_first(client, seed):
    response = client.get("/orders")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == len(seed["orders"])
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert len(payload["items"]) == 20
    assert payload["items"][0]["id"] == max(order["id"] for order in seed["orders"])


def test_get_order_by_id(client, seed):
    response = client.get("/orders/A-1001")
    assert response.status_code == 200
    assert response.json()["id"] == "A-1001"


def test_unknown_order(client):
    response = client.get("/orders/NOT-REAL")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_valid_order_transitions(client, seed):
    order_id = "A-1001"
    for current, next_status in [
        ("placed", "shipped"),
        ("shipped", "delivered"),
        ("delivered", "returned"),
        ("returned", "refunded"),
    ]:
        response = client.patch(
            f"/orders/{order_id}/status", json={"status": next_status}
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == next_status
        response = client.get(f"/orders/{order_id}")
        assert response.json()["status"] == next_status


def test_invalid_order_transition_skips_steps(client):
    response = client.patch("/orders/A-1001/status", json={"status": "delivered"})
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "Cannot change status from 'placed' to 'delivered'"
    )


def test_order_backward_transition_is_rejected(client):
    response = client.patch("/orders/A-1001/status", json={"status": "placed"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot change status from 'placed' to 'placed'"


def test_order_same_status_is_rejected(client):
    response = client.patch("/orders/A-1001/status", json={"status": "placed"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot change status from 'placed' to 'placed'"


def test_refunded_order_rejects_any_change(client):
    response = client.patch("/orders/A-2000/status", json={"status": "shipped"})
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "Cannot change status from 'refunded' to 'shipped'"
    )


def test_unknown_order_status_value(client):
    response = client.patch("/orders/A-1001/status", json={"status": "unknown"})
    assert response.status_code == 422

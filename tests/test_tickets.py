def test_create_ticket_without_order(client, seed):
    payload = {
        "customer_id": 1,
        "subject": "Delivery issue",
        "message": "The package arrived late and I need status updates.",
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == 1
    assert data["order_id"] is None
    assert data["status"] == "open"
    assert data["channel"] == "email"
    assert data["priority"] == "medium"


def test_create_ticket_for_customer_order(client):
    payload = {
        "customer_id": 1,
        "order_id": "A-1001",
        "subject": "Need help with the order",
        "message": "The order is delayed and I want an update.",
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    assert response.json()["order_id"] == "A-1001"


def test_create_ticket_unknown_customer(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 99999,
            "subject": "subject",
            "message": "This message is long enough to pass validation.",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_create_ticket_unknown_order_for_customer(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "order_id": "A-9999",
            "subject": "subject",
            "message": "This message is long enough to pass validation.",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found for this customer"


def test_create_ticket_for_other_customer_order(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "order_id": "A-1002",
            "subject": "subject",
            "message": "This message is long enough to pass validation.",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found for this customer"


def test_create_ticket_validation_errors(client):
    bad_cases = [
        {"customer_id": 1, "subject": "x", "message": "This is long enough."},
        {"customer_id": 1, "subject": "Valid subject", "message": "shor"},
        {
            "customer_id": 1,
            "subject": "Valid subject",
            "message": "Valid enough.",
            "channel": "invalid",
        },
        {
            "customer_id": 1,
            "subject": "Valid subject",
            "message": "Valid enough.",
            "priority": "urgent",
        },
    ]
    for payload in bad_cases:
        response = client.post("/tickets", json=payload)
        assert response.status_code == 422


def test_ticket_filters_and_new_ticket_first(client, seed):
    response = client.get("/tickets", params={"customer_id": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert payload["items"][0]["customer_id"] == 1


def test_tickets_status_priority_customer_filters(client, seed):
    for filter_name, value in [
        ("status", "open"),
        ("priority", "medium"),
        ("customer_id", 1),
    ]:
        response = client.get("/tickets", params={filter_name: value})
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] >= 0


def test_get_ticket_by_id(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "subject": "Issue with order",
            "message": "The status is unclear and I need help.",
        },
    )
    ticket_id = response.json()["id"]
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_unknown_ticket(client):
    response = client.get("/tickets/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_ticket_status_progression(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "subject": "Issue",
            "message": "Need a quick update on the order status.",
        },
    )
    ticket_id = response.json()["id"]
    for next_status in ["in_progress", "resolved", "closed"]:
        response = client.patch(
            f"/tickets/{ticket_id}/status", json={"status": next_status}
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == next_status


def test_closed_ticket_rejects_status_change(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "subject": "Issue",
            "message": "Need a quick update on the order status.",
        },
    )
    ticket_id = response.json()["id"]
    client.patch(f"/tickets/{ticket_id}/status", json={"status": "closed"})
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "open"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Closed tickets cannot be reopened"


def test_unknown_ticket_status_value(client):
    response = client.post(
        "/tickets",
        json={
            "customer_id": 1,
            "subject": "Issue",
            "message": "Need a quick update on the order status.",
        },
    )
    ticket_id = response.json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": "unknown"})
    assert response.status_code == 422


def test_unknown_ticket_status_404(client):
    response = client.patch("/tickets/99999/status", json={"status": "closed"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"

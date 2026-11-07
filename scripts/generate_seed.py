from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = ROOT / "data" / "seed.json"

CITY_STATE = {
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Pune": "Maharashtra",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Ahmedabad": "Gujarat",
}

PRODUCTS = {
    "fashion": [
        "Cotton Kurta",
        "Silk Saree",
        "Printed Dupatta",
        "Festive Lehenga",
        "Classic Nehru Jacket",
    ],
    "home_kitchen": [
        "Cookware Set",
        "Pressure Cooker",
        "Blender",
        "Rice Cooker",
        "Induction Base Pan",
    ],
    "electronics": [
        "Smartphone",
        "Bluetooth Speaker",
        "Wireless Earbuds",
        "Smartwatch",
        "Tablet",
    ],
    "accessories": [
        "Leather Wallet",
        "Sunglasses",
        "Travel Bag",
        "Laptop Sleeve",
        "Silk Scarf",
    ],
    "sports": [
        "Cricket Bat",
        "Badminton Racket",
        "Yoga Mat",
        "Running Shoes",
        "Gym Bag",
    ],
    "books": [
        "JEE Workbook",
        "Civil Services Guide",
        "Novel Bundle",
        "Exam Prep Pack",
        "Story Collection",
    ],
    "beauty": [
        "Face Serum",
        "Lip Balm Set",
        "Compact Mirror",
        "Hair Oil",
        "Skincare Kit",
    ],
}

ORDER_STATUSES = ["placed", "shipped", "delivered", "returned", "refunded"]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high"]
CHANNELS = ["email", "chat", "whatsapp", "phone"]
CATEGORIES = list(PRODUCTS)


def make_customer(index: int) -> dict:
    city = list(CITY_STATE)[index % len(CITY_STATE)]
    base = datetime(2025, 1, 1) + timedelta(days=index * 2, hours=index % 12)
    return {
        "id": index,
        "name": f"Customer {index}",
        "email": f"customer{index}@acme.example",
        "phone": f"+91 9{(100000000 + index):09d}",
        "city": city,
        "state": CITY_STATE[city],
        "created_at": base.isoformat(timespec="seconds"),
    }


def make_order(index: int) -> dict:
    customer_id = ((index - 1) % 200) + 1
    category = CATEGORIES[(index - 1) % len(CATEGORIES)]
    product = PRODUCTS[category][(index - 1) % len(PRODUCTS[category])]
    status = ORDER_STATUSES[(index - 1) % len(ORDER_STATUSES)]
    created_at = datetime(2026, 3, 1) + timedelta(
        days=index - 1,
        hours=(index * 3) % 24,
        minutes=(index * 7) % 60,
    )
    return {
        "id": f"A-{1000 + index}",
        "customer_id": customer_id,
        "product": product,
        "category": category,
        "quantity": (index % 5) + 1,
        "amount_inr": round((index * 149.5) % 5600 + 499, 2),
        "payment_method": ["UPI", "Card", "Cash on Delivery", "Net Banking", "Wallet"][
            index % 5
        ],
        "status": status,
        "created_at": created_at.isoformat(timespec="seconds"),
    }


def make_ticket(index: int) -> dict:
    customer_id = ((index - 1) % 200) + 1
    order_id = f"A-{1000 + ((index - 1) % 1000) + 1}" if index % 3 == 0 else None
    if order_id is not None and ((index - 1) % 200) + 1 != customer_id:
        order_id = None
    created_at = datetime(2026, 3, 1) + timedelta(
        days=(index - 1) % 30,
        hours=(index * 2) % 24,
        minutes=(index * 11) % 60,
    )
    return {
        "id": index,
        "customer_id": customer_id,
        "order_id": order_id,
        "subject": f"Ticket {index}: support request",
        "message": f"Customer {customer_id} needs support for ticket {index}. Please help resolve this issue quickly.",
        "channel": CHANNELS[(index - 1) % len(CHANNELS)],
        "priority": PRIORITIES[(index - 1) % len(PRIORITIES)],
        "status": TICKET_STATUSES[(index - 1) % len(TICKET_STATUSES)],
        "created_at": created_at.isoformat(timespec="seconds"),
    }


def main() -> None:
    customers = [make_customer(i) for i in range(1, 201)]
    orders = [make_order(i) for i in range(1, 1001)]
    tickets = [make_ticket(i) for i in range(1, 301)]

    payload = {"customers": customers, "orders": orders, "tickets": tickets}
    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SEED_PATH.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()

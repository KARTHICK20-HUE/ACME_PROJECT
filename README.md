# Acme Support Copilot

Acme Support Copilot is a FastAPI backend for the fictional Indian retailer Acme. It exposes customer lookup, order lifecycle management, and support ticket workflows for the customer-support team, with a SQLite-backed data model and seed data that mirrors the project specification.

## Run the app

From the project root, create or activate the virtual environment and start the API:

```bash
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload
```

Then open the interactive API docs at http://127.0.0.1:8000/docs.

## Run the tests

```bash
source .venv/bin/activate
PYTHONPATH=. pytest -q
PYTHONPATH=. ruff check .
```

## Seed data

The project includes a   generated seed file at [data/seed.json](data/seed.json). This file is intentionally used as the canonical dataset for the application and should not be edited by hand. The generator can be re-run with:

```bash
source .venv/bin/activate
PYTHONPATH=. python scripts/generate_seed.py
```

## Endpoints

| Tag | Routes |
| --- | --- |
| health | GET /health |
| customers | GET /customers, GET /customers/{customer_id}, GET /customers/{customer_id}/orders |
| orders | GET /orders, GET /orders/search, GET /orders/{order_id}, PATCH /orders/{order_id}/status |
| tickets | POST /tickets, GET /tickets, GET /tickets/{ticket_id}, PATCH /tickets/{ticket_id}/status |

## Pagination response shape

Every paginated list endpoint returns a payload shaped like this:

```json
{
  "items": [
    {"id": "A-1001", "customer_id": 1, "status": "placed"}
  ],
  "total": 1000,
  "page": 1,
  "page_size": 20
}
```

## Project layout

```text
.
├── .github/
│   └── copilot-instructions.md
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   ├── pagination.py
│   │   └── tickets.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
├── data/
│   └── seed.json
├── scripts/
│   └── generate_seed.py
├── specs/
│   └── acme_backend_spec.md
├── tests/
│   ├── conftest.py
│   ├── test_customers.py
│   ├── test_health.py
│   ├── test_order_search.py
│   ├── test_orders.py
│   └── test_tickets.py
├── .gitignore
├── README.md
├── requirements.txt
└── acme.db
```
##Karthick
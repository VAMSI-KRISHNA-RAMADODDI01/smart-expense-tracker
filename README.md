# Smart Expense Tracker API

A small REST API for tracking personal expenses, built with **FastAPI**.
Data is kept in memory and mirrored to a local JSON file (`data/expenses.json`)
so it survives a server restart. No database is required.

## Features

- `POST /expenses` — add an expense (`title`, `amount`, `category`, `date`)
- `GET /expenses` — list all expenses
- `GET /expenses?category=Food` — filter expenses by category (case-insensitive)
- `GET /expenses/totals` — overall total and total per category
- `DELETE /expenses/{id}` — delete an expense by id
- **Bonus:** interactive OpenAPI/Swagger docs, auto-generated at `/docs` (and `/redoc`)

## Requirements

- Python 3.10+

## Install

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server

```bash
python -m uvicorn src.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`.

### Example requests

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Groceries","amount":45.50,"category":"Food","date":"2026-07-01"}'

curl http://127.0.0.1:8000/expenses
curl "http://127.0.0.1:8000/expenses?category=Food"
curl http://127.0.0.1:8000/expenses/totals
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

## Run the tests

```bash
pytest
```

All 13 tests should pass. Tests reset the in-memory store before and after
each test, so they don't depend on each other or on the server actually
running (they use FastAPI's `TestClient`, which drives the app in-process).

## Project structure

```
.
├── README.md
├── AI_NOTES.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py        # FastAPI app and route definitions
│   ├── models.py       # Pydantic request/response models
│   └── storage.py      # In-memory store with JSON file persistence
├── tests/
│   ├── __init__.py
│   └── test_api.py
└── data/
    └── expenses.json    # Created/updated automatically at runtime
```

## Design notes

- IDs are server-assigned, auto-incrementing integers. Deleted IDs are never reused.
- `amount` must be a positive number; `title`/`category` cannot be blank; `date` must
  be a valid ISO date (`YYYY-MM-DD`) — all enforced by Pydantic validation, returning
  `422` on bad input.
- Deleting a non-existent id returns `404`, not a silent no-op.
- Category filtering is case-insensitive (`?category=food` matches `"Food"`).

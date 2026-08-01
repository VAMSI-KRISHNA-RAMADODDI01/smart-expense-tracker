"""
Test suite for the Smart Expense Tracker API.

Run with: pytest
Each test resets the store first so tests don't leak state into each other.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    """Guarantee every test starts from an empty store."""
    store.reset()
    yield
    store.reset()


SAMPLE_EXPENSE = {
    "title": "Groceries",
    "amount": 45.50,
    "category": "Food",
    "date": "2026-07-01",
}


def test_add_expense_returns_created_expense_with_id():
    resp = client.post("/expenses", json=SAMPLE_EXPENSE)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["title"] == "Groceries"
    assert body["amount"] == 45.50
    assert body["category"] == "Food"
    assert body["date"] == "2026-07-01"


def test_add_expense_rejects_non_positive_amount():
    bad = {**SAMPLE_EXPENSE, "amount": 0}
    resp = client.post("/expenses", json=bad)
    assert resp.status_code == 422

    bad_negative = {**SAMPLE_EXPENSE, "amount": -10}
    resp = client.post("/expenses", json=bad_negative)
    assert resp.status_code == 422


def test_add_expense_rejects_blank_title():
    bad = {**SAMPLE_EXPENSE, "title": "   "}
    resp = client.post("/expenses", json=bad)
    assert resp.status_code == 422


def test_add_expense_rejects_invalid_date():
    bad = {**SAMPLE_EXPENSE, "date": "not-a-date"}
    resp = client.post("/expenses", json=bad)
    assert resp.status_code == 422


def test_list_expenses_empty_initially():
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_expenses_returns_all_added():
    client.post("/expenses", json=SAMPLE_EXPENSE)
    client.post("/expenses", json={**SAMPLE_EXPENSE, "title": "Bus ticket", "category": "Travel"})
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_filter_by_category_case_insensitive():
    client.post("/expenses", json=SAMPLE_EXPENSE)  # category "Food"
    client.post("/expenses", json={**SAMPLE_EXPENSE, "title": "Taxi", "category": "Travel"})

    resp = client.get("/expenses", params={"category": "food"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Groceries"


def test_filter_by_category_no_matches_returns_empty_list():
    client.post("/expenses", json=SAMPLE_EXPENSE)
    resp = client.get("/expenses", params={"category": "Nonexistent"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_totals_with_no_expenses():
    resp = client.get("/expenses/totals")
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_total"] == 0
    assert body["by_category"] == []


def test_totals_overall_and_by_category():
    client.post("/expenses", json={**SAMPLE_EXPENSE, "amount": 50, "category": "Food"})
    client.post("/expenses", json={**SAMPLE_EXPENSE, "amount": 30, "category": "Food"})
    client.post("/expenses", json={**SAMPLE_EXPENSE, "amount": 20, "category": "Travel"})

    resp = client.get("/expenses/totals")
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_total"] == 100

    by_category = {c["category"]: c["total"] for c in body["by_category"]}
    assert by_category["Food"] == 80
    assert by_category["Travel"] == 20


def test_delete_expense_removes_it():
    created = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    expense_id = created["id"]

    resp = client.delete(f"/expenses/{expense_id}")
    assert resp.status_code == 204

    resp = client.get("/expenses")
    assert resp.json() == []


def test_delete_nonexistent_expense_returns_404():
    resp = client.delete("/expenses/9999")
    assert resp.status_code == 404


def test_deleted_id_is_not_reused():
    """Deleting expense 1 and adding a new one should not reuse id 1."""
    first = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    client.delete(f"/expenses/{first['id']}")
    second = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    assert second["id"] != first["id"]

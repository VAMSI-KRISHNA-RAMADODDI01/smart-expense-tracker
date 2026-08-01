"""
Simple persistence layer for expenses.

Expenses are kept in memory for fast access, and mirrored to a JSON file
on every write so data survives a server restart. No database is used,
per the assignment's requirements.
"""
import json
import threading
from pathlib import Path
from datetime import date
from typing import Optional

from .models import Expense, ExpenseCreate

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "expenses.json"


class ExpenseStore:
    def __init__(self, data_file: Path = DATA_FILE):
        self._data_file = data_file
        self._lock = threading.Lock()
        self._expenses: dict[int, Expense] = {}
        self._next_id = 1
        self._load()

    # ---------- persistence ----------

    def _load(self) -> None:
        if not self._data_file.exists():
            return
        try:
            raw = json.loads(self._data_file.read_text())
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file: start fresh rather than crash the app.
            return
        for item in raw:
            expense = Expense(**item)
            self._expenses[expense.id] = expense
        if self._expenses:
            self._next_id = max(self._expenses) + 1

    def _persist(self) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [json.loads(e.model_dump_json()) for e in self._expenses.values()]
        self._data_file.write_text(json.dumps(payload, indent=2, default=str))

    # ---------- CRUD ----------

    def add(self, data: ExpenseCreate) -> Expense:
        with self._lock:
            expense = Expense(id=self._next_id, **data.model_dump())
            self._expenses[expense.id] = expense
            self._next_id += 1
            self._persist()
            return expense

    def list_all(self, category: Optional[str] = None) -> list[Expense]:
        items = list(self._expenses.values())
        if category is not None:
            items = [e for e in items if e.category.lower() == category.lower()]
        return sorted(items, key=lambda e: e.id)

    def delete(self, expense_id: int) -> bool:
        with self._lock:
            if expense_id not in self._expenses:
                return False
            del self._expenses[expense_id]
            self._persist()
            return True

    def totals(self) -> tuple[float, dict[str, float]]:
        by_category: dict[str, float] = {}
        overall = 0.0
        for e in self._expenses.values():
            overall += e.amount
            by_category[e.category] = by_category.get(e.category, 0.0) + e.amount
        return round(overall, 2), {k: round(v, 2) for k, v in by_category.items()}

    def reset(self) -> None:
        """Used by tests to guarantee a clean slate."""
        with self._lock:
            self._expenses.clear()
            self._next_id = 1
            self._persist()

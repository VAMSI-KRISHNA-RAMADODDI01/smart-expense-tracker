"""Pydantic models for the Smart Expense Tracker API."""
from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    """Payload for creating a new expense. `id` is assigned by the server."""

    title: str = Field(..., min_length=1, description="Short description of the expense")
    amount: float = Field(..., gt=0, description="Expense amount, must be positive")
    category: str = Field(..., min_length=1, description="e.g. Food, Travel, Rent")
    date: date_type = Field(..., description="Date the expense occurred, ISO format YYYY-MM-DD")

    @field_validator("title", "category")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank or whitespace")
        return v.strip()


class Expense(ExpenseCreate):
    """A stored expense, including its server-assigned id."""

    id: int


class CategoryTotal(BaseModel):
    category: str
    total: float


class TotalsResponse(BaseModel):
    overall_total: float
    by_category: list[CategoryTotal]

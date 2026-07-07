from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator


DB_PATH = Path(__file__).with_name("expenses.db")


@dataclass(frozen=True)
class ExpenseRow:
    amount: float
    category: str
    expense_date: str


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                entry_type TEXT NOT NULL DEFAULT 'expense',
                expense_date TEXT NOT NULL
            )
            """
        )
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(transactions)").fetchall()
        }
        if "entry_type" not in existing_columns:
            conn.execute(
                "ALTER TABLE transactions ADD COLUMN entry_type TEXT NOT NULL DEFAULT 'expense'"
            )


def add_transaction(
    amount: float,
    category: str,
    entry_type: str,
    expense_date: str | None = None,
) -> None:
    expense_date = expense_date or date.today().isoformat()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO transactions (amount, category, entry_type, expense_date)
            VALUES (?, ?, ?, ?)
            """,
            (amount, category.strip().title(), entry_type, expense_date),
        )


def add_expense(amount: float, category: str, expense_date: str | None = None) -> None:
    add_transaction(amount, category, "expense", expense_date)


def add_income(amount: float, category: str, expense_date: str | None = None) -> None:
    add_transaction(amount, category, "income", expense_date)


def get_daily_summary(expense_date: str | None = None) -> list[ExpenseRow]:
    expense_date = expense_date or date.today().isoformat()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS amount, expense_date
            FROM transactions
            WHERE expense_date = ? AND entry_type = 'expense'
            GROUP BY category, expense_date
            ORDER BY amount DESC, category ASC
            """,
            (expense_date,),
        ).fetchall()

    return [
        ExpenseRow(amount=float(row["amount"]), category=row["category"], expense_date=row["expense_date"])
        for row in rows
    ]


def get_daily_income_summary(expense_date: str | None = None) -> list[ExpenseRow]:
    expense_date = expense_date or date.today().isoformat()
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS amount, expense_date
            FROM transactions
            WHERE expense_date = ? AND entry_type = 'income'
            GROUP BY category, expense_date
            ORDER BY amount DESC, category ASC
            """,
            (expense_date,),
        ).fetchall()

    return [
        ExpenseRow(amount=float(row["amount"]), category=row["category"], expense_date=row["expense_date"])
        for row in rows
    ]


def get_month_summary(year_month: str) -> list[ExpenseRow]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS amount, substr(expense_date, 1, 7) AS expense_month
            FROM transactions
            WHERE substr(expense_date, 1, 7) = ? AND entry_type = 'expense'
            GROUP BY category, expense_month
            ORDER BY amount DESC, category ASC
            """,
            (year_month,),
        ).fetchall()

    return [
        ExpenseRow(amount=float(row["amount"]), category=row["category"], expense_date=row["expense_month"])
        for row in rows
    ]


def get_month_income_summary(year_month: str) -> list[ExpenseRow]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT category, SUM(amount) AS amount, substr(expense_date, 1, 7) AS expense_month
            FROM transactions
            WHERE substr(expense_date, 1, 7) = ? AND entry_type = 'income'
            GROUP BY category, expense_month
            ORDER BY amount DESC, category ASC
            """,
            (year_month,),
        ).fetchall()

    return [
        ExpenseRow(amount=float(row["amount"]), category=row["category"], expense_date=row["expense_month"])
        for row in rows
    ]


def get_total_for_day(expense_date: str | None = None) -> float:
    expense_date = expense_date or date.today().isoformat()
    with connect() as conn:
        value = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE expense_date = ? AND entry_type = 'expense'
            """,
            (expense_date,),
        ).fetchone()["total"]
    return float(value)


def get_daily_income_total(expense_date: str | None = None) -> float:
    expense_date = expense_date or date.today().isoformat()
    with connect() as conn:
        value = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE expense_date = ? AND entry_type = 'income'
            """,
            (expense_date,),
        ).fetchone()["total"]
    return float(value)


def get_total_for_month(year_month: str) -> float:
    with connect() as conn:
        value = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE substr(expense_date, 1, 7) = ? AND entry_type = 'expense'
            """,
            (year_month,),
        ).fetchone()["total"]
    return float(value)


def get_month_income_total(year_month: str) -> float:
    with connect() as conn:
        value = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE substr(expense_date, 1, 7) = ? AND entry_type = 'income'
            """,
            (year_month,),
        ).fetchone()["total"]
    return float(value)

from datetime import date
from pathlib import Path

import pytest

from finance_analyzer import Account, Transaction

DATA = Path(__file__).parent.parent / "data"


def small_account() -> Account:
    return Account(
        [
            Transaction(date(2025, 10, 1), "Rent", -800.0),
            Transaction(date(2025, 10, 25), "Salary", 1000.0),
            Transaction(date(2025, 11, 2), "Lidl", -50.0),
        ],
        starting_balance=100.0,
    )


def test_balance():
    account = small_account()

    assert account.total_income == 1000.0
    assert account.total_expenses == -850.0
    assert account.balance == 250.0


def test_monthly_summary():
    summary = small_account().monthly_summary()

    assert list(summary["net"]) == [200.0, -50.0]


def test_spending_by_category_biggest_first():
    spending = small_account().spending_by_category()

    assert list(spending.index) == ["Housing", "Groceries"]
    assert spending["Housing"] == 800.0


def test_sample_file():
    account = Account.from_csv(DATA / "sample_transactions.csv", starting_balance=1000)

    assert len(account) == 379
    assert account.balance == pytest.approx(6296.85)
    assert account.skipped_rows == []

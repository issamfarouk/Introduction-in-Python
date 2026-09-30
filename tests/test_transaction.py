from datetime import date

import pytest

from finance_analyzer import Transaction


def test_income_and_expense():
    salary = Transaction(date(2025, 10, 25), "Salary", 2100.0)
    rent = Transaction(date(2025, 10, 1), "Rent", -750.0)

    assert salary.is_income and not salary.is_expense
    assert rent.is_expense and not rent.is_income


def test_empty_description_is_rejected():
    with pytest.raises(ValueError):
        Transaction(date(2025, 10, 1), "   ", -5.0)


def test_sorted_by_date():
    later = Transaction(date(2025, 10, 25), "Salary", 2100.0)
    earlier = Transaction(date(2025, 10, 1), "Rent", -750.0)

    assert sorted([later, earlier]) == [earlier, later]

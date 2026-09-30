from datetime import date

from finance_analyzer import Account, Transaction, get_advice


def losing_account() -> Account:
    return Account(
        [
            Transaction(date(2025, 10, 1), "Salary", 1000.0),
            Transaction(date(2025, 10, 2), "Rent", -800.0),
            Transaction(date(2025, 11, 1), "Salary", 1000.0),
            Transaction(date(2025, 11, 2), "Laptop", -1500.0),
        ]
    )


def test_losing_month_and_negative_balance():
    tips = "\n".join(get_advice(losing_account()))

    assert "In 2025-11 you spent 500.00 € more than you earned" in tips
    assert "Your balance is -300.00 €" in tips
    assert "saved only -" not in tips


def test_forecast_months_are_used():
    tips = get_advice(losing_account(), forecast_months=12)

    assert "In 12 months" in tips[-1]

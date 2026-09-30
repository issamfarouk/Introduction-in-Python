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


def test_price_increase_tip():
    months = [(2025, 10), (2025, 11), (2025, 12), (2026, 1)]
    prices = [-9.99, -9.99, -10.99, -10.99]
    account = Account(
        [
            Transaction(date(year, month, 1), "Music", price)
            for (year, month), price in zip(months, prices)
        ]
    )
    tips = "\n".join(get_advice(account))

    assert "Music went from 9.99 € to 10.99 € (12.00 € more per year)" in tips


def test_no_price_increase_tip_when_prices_stay_the_same():
    tips = "\n".join(get_advice(losing_account()))

    assert "Price increase" not in tips


def test_forecast_months_are_used():
    tips = get_advice(losing_account(), forecast_months=12)

    assert "In 12 months" in tips[-1]

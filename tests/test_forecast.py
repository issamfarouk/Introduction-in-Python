from datetime import date

import pytest

from finance_analyzer import Account, Transaction, forecast_balance


def test_straight_line():
    # Save exactly 100 € every month, so the balance grows by 100 per month
    account = Account(
        [Transaction(date(2025, month, 1), "Salary", 100.0) for month in (1, 2, 3)]
    )
    forecast = forecast_balance(account, months=2)

    assert list(forecast.round(2)) == [400.0, 500.0]
    assert str(forecast.index[0]) == "2025-04"


def test_needs_two_months():
    account = Account([Transaction(date(2025, 1, 1), "Salary", 100.0)])

    with pytest.raises(ValueError):
        forecast_balance(account)

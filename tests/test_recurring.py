from datetime import date, timedelta
from pathlib import Path

from finance_analyzer import Account, Transaction, find_recurring

DATA = Path(__file__).parent.parent / "data"


def test_finds_the_monthly_payments_in_the_sample():
    account = Account.from_csv(DATA / "sample_transactions.csv")
    names = {payment.description for payment in find_recurring(account)}

    assert names == {
        "Rent",
        "Netflix",
        "Deutschlandticket",
        "FitX Gym",
        "Vodafone Mobile",
        "Spotify",
        "Salary",
    }


def test_weekly_payment():
    start = date(2025, 10, 6)
    account = Account(
        [Transaction(start + timedelta(weeks=i), "Cleaning", -40.0) for i in range(5)]
    )
    payment = find_recurring(account)[0]

    assert payment.interval == "weekly"
    assert payment.yearly_amount == -40.0 * 52


def test_changing_amounts_are_not_recurring():
    account = Account(
        [
            Transaction(date(2025, 10, 1), "Lidl", -10.0),
            Transaction(date(2025, 11, 1), "Lidl", -55.0),
            Transaction(date(2025, 12, 1), "Lidl", -30.0),
        ]
    )

    assert find_recurring(account) == []

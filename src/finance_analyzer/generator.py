"""Create realistic fake bank transactions for testing and demos."""

import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from finance_analyzer.transaction import Transaction

# Payments that happen every month on the same day: (day, description, amount)
MONTHLY_PAYMENTS = [
    (1, "Rent", -750.00),
    (1, "Netflix", -12.99),
    (3, "Deutschlandticket", -58.00),
    (5, "FitX Gym", -24.99),
    (10, "Vodafone Mobile", -19.99),
    (15, "Spotify", -10.99),
    (25, "Salary", 2100.00),
]

# Subscriptions that get more expensive: description -> (months after start, new amount)
PRICE_INCREASES = {
    "Netflix": (6, -13.99),
}

# Everyday shops: description -> (smallest amount, biggest amount)
RANDOM_SHOPS = {
    "Lidl": (8, 60),
    "Rewe": (10, 80),
    "Aldi": (5, 50),
    "dm Drogerie": (5, 30),
    "Starbucks": (4, 9),
    "Pizza Hut": (12, 35),
    "Amazon": (15, 120),
}


def add_months(start: date, months: int) -> date:
    """Return the first day of the month that is `months` after `start`."""
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    return date(year, month, 1)


def generate_transactions(
    start: date = date(2025, 10, 1),
    months: int = 12,
    seed: int = 42,
) -> list[Transaction]:
    """Create fake transactions for `months` months, starting at `start`.

    The same `seed` always gives the same transactions.
    """
    rng = np.random.default_rng(seed)
    shop_names = list(RANDOM_SHOPS)
    end = add_months(start, months)

    transactions = []
    day = start
    while day < end:
        # Fixed monthly payments
        for pay_day, description, amount in MONTHLY_PAYMENTS:
            if day.day == pay_day:
                if description in PRICE_INCREASES:
                    months_later, new_amount = PRICE_INCREASES[description]
                    if day >= add_months(start, months_later):
                        amount = new_amount
                transactions.append(Transaction(day, description, amount))

        # Random everyday shopping (on average less than one purchase per day)
        for _ in range(rng.poisson(0.8)):
            shop = str(rng.choice(shop_names))
            low, high = RANDOM_SHOPS[shop]
            amount = -round(float(rng.uniform(low, high)), 2)
            transactions.append(Transaction(day, shop, amount))

        day += timedelta(days=1)

    return sorted(transactions)


def save_to_csv(transactions: list[Transaction], path: Path) -> None:
    """Write transactions to a CSV file like a bank export."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Description", "Amount"])
        for t in transactions:
            writer.writerow([t.date.isoformat(), t.description, f"{t.amount:.2f}"])

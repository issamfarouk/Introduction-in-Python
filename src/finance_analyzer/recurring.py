"""Find payments that repeat regularly, like subscriptions, rent, or salary."""

import numpy as np

from finance_analyzer.account import Account

# Name -> (shortest gap in days, longest gap in days, times per year)
INTERVALS = {
    "weekly": (6, 8, 52),
    "monthly": (26, 35, 12),
    "yearly": (355, 375, 1),
}


class RecurringPayment:
    """A payment that happens again and again with (almost) the same amount."""

    def __init__(
        self,
        description: str,
        amount: float,
        interval: str,
        day_of_month: int,
        occurrences: int,
    ) -> None:
        self.description = description
        self.amount = amount
        self.interval = interval
        self.day_of_month = day_of_month
        self.occurrences = occurrences

    @property
    def yearly_amount(self) -> float:
        """How much this payment adds up to over one year."""
        times_per_year = INTERVALS[self.interval][2]
        return self.amount * times_per_year

    def __repr__(self) -> str:
        return (
            f"RecurringPayment({self.description!r}, {self.amount}, "
            f"{self.interval!r}, {self.day_of_month}, {self.occurrences})"
        )

    def __str__(self) -> str:
        return (
            f"{self.description:<20} {self.amount:>9.2f} € {self.interval:<8} "
            f"(around day {self.day_of_month:>2}, {self.yearly_amount:>9.2f} € per year)"
        )


def interval_name(days: float) -> str | None:
    """Turn an average gap in days into 'weekly', 'monthly', ... or None."""
    for name, (shortest, longest, _) in INTERVALS.items():
        if shortest <= days <= longest:
            return name
    return None


def find_recurring(
    account: Account,
    min_occurrences: int = 3,
    amount_tolerance: float = 0.05,
) -> list[RecurringPayment]:
    """Find all recurring payments in an account.

    A payment counts as recurring when it
    1. happens at least `min_occurrences` times,
    2. always has about the same amount (within `amount_tolerance`, 5% by default),
    3. happens at regular intervals (weekly, monthly, or yearly).
    """
    df = account.to_dataframe()
    found = []

    for _, group in df.groupby(df["description"].str.lower()):
        # 1. Often enough?
        if len(group) < min_occurrences:
            continue

        # 2. Same amount every time?
        amounts = group["amount"].to_numpy()
        average = amounts.mean()
        if np.abs(amounts - average).max() > abs(average) * amount_tolerance:
            continue

        # 3. Regular gaps between the dates?
        gaps_in_days = np.diff(group["date"].to_numpy()) / np.timedelta64(1, "D")
        interval = interval_name(float(np.median(gaps_in_days)))
        if interval is None:
            continue

        found.append(
            RecurringPayment(
                description=group["description"].iloc[0],
                amount=round(float(average), 2),
                interval=interval,
                day_of_month=int(group["date"].dt.day.mode()[0]),
                occurrences=len(group),
            )
        )

    # Biggest costs first, income last
    return sorted(found, key=lambda payment: payment.amount)

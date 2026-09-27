"""The Transaction class: a single line from a bank statement."""

from datetime import date


class Transaction:
    """A single bank transaction (money in or money out)."""

    def __init__(
        self,
        when: date,
        description: str,
        amount: float,
        category: str = "Uncategorized",
    ) -> None:
        if not description.strip():
            raise ValueError("A transaction needs a description")

        self.date = when
        self.description = description.strip()
        self.amount = amount
        self.category = category

    @property
    def is_income(self) -> bool:
        """True if money came in (positive amount)."""
        return self.amount > 0

    @property
    def is_expense(self) -> bool:
        """True if money went out (negative amount)."""
        return self.amount < 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return NotImplemented
        return (
            self.date == other.date
            and self.description == other.description
            and self.amount == other.amount
        )

    def __lt__(self, other: "Transaction") -> bool:
        return self.date < other.date

    def __repr__(self) -> str:
        return (
            f"Transaction({self.date!r}, {self.description!r}, "
            f"{self.amount}, {self.category!r})"
        )

    def __str__(self) -> str:
        return f"{self.date}  {self.description:<20} {self.amount:>10.2f} €"

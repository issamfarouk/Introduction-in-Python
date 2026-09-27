"""The Account class: all transactions of one bank account."""

from pathlib import Path

import pandas as pd

from finance_analyzer.importers import load_transactions
from finance_analyzer.transaction import Transaction


class Account:
    """A bank account made of many transactions."""

    def __init__(
        self,
        transactions: list[Transaction],
        starting_balance: float = 0.0,
    ) -> None:
        self.transactions = sorted(transactions)
        self.starting_balance = starting_balance

    @classmethod
    def from_csv(cls, path: str | Path, starting_balance: float = 0.0) -> "Account":
        """Create an account directly from a bank statement file."""
        return cls(load_transactions(path), starting_balance)

    @property
    def total_income(self) -> float:
        return sum(t.amount for t in self.transactions if t.is_income)

    @property
    def total_expenses(self) -> float:
        return sum(t.amount for t in self.transactions if t.is_expense)

    @property
    def balance(self) -> float:
        """Money in the account after the last transaction."""
        return self.starting_balance + self.total_income + self.total_expenses

    def to_dataframe(self) -> pd.DataFrame:
        """All transactions as a table, with the running balance after each one."""
        df = pd.DataFrame(
            {
                "date": [t.date for t in self.transactions],
                "description": [t.description for t in self.transactions],
                "amount": [t.amount for t in self.transactions],
                "category": [t.category for t in self.transactions],
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        df["balance"] = self.starting_balance + df["amount"].cumsum()
        return df

    def monthly_summary(self) -> pd.DataFrame:
        """Income, expenses and savings (net) for every month."""
        df = self.to_dataframe()
        income = df[df["amount"] > 0].groupby("month")["amount"].sum()
        expenses = df[df["amount"] < 0].groupby("month")["amount"].sum()

        summary = pd.DataFrame({"income": income, "expenses": expenses}).fillna(0.0)
        summary["net"] = summary["income"] + summary["expenses"]
        return summary

    def __len__(self) -> int:
        return len(self.transactions)

    def __repr__(self) -> str:
        return f"Account({len(self)} transactions, balance={self.balance:.2f})"

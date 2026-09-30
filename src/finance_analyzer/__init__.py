"""finance_analyzer: analyze bank transactions and get saving tips.

Example:
    >>> from finance_analyzer import Account, get_advice
    >>> account = Account.from_csv("data/sample_transactions.csv", starting_balance=1000)
    >>> for tip in get_advice(account):
    ...     print(tip)
"""

from finance_analyzer.account import Account
from finance_analyzer.advisor import get_advice
from finance_analyzer.categorizer import categorize
from finance_analyzer.forecast import forecast_balance
from finance_analyzer.generator import generate_transactions
from finance_analyzer.importers import StatementError, load_transactions
from finance_analyzer.plots import save_all_plots
from finance_analyzer.recurring import RecurringPayment, find_recurring
from finance_analyzer.report import build_report
from finance_analyzer.transaction import Transaction

__all__ = [
    "Account",
    "RecurringPayment",
    "StatementError",
    "Transaction",
    "build_report",
    "categorize",
    "find_recurring",
    "forecast_balance",
    "generate_transactions",
    "get_advice",
    "load_transactions",
    "save_all_plots",
]

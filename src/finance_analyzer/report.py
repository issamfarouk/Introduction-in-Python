"""Put every analysis together into one readable text report."""

from finance_analyzer.account import Account
from finance_analyzer.advisor import get_advice
from finance_analyzer.forecast import forecast_balance, month_end_balances
from finance_analyzer.recurring import find_recurring


def _heading(title: str) -> str:
    return f"\n{title}\n{'-' * len(title)}"


def _euro(value: float) -> str:
    return f"{value:,.2f} €"


def build_report(account: Account, name: str = "Account", forecast_months: int = 6) -> str:
    """Return the full report as one string (ready to print or save)."""
    lines = [f"💰 Finance report: {name}", "=" * 40]

    if len(account) == 0:
        lines.append("No transactions found.")
        return "\n".join(lines)

    first, last = account.transactions[0].date, account.transactions[-1].date
    lines += [
        f"Transactions:     {len(account)} ({first} to {last})",
        f"Starting balance: {_euro(account.starting_balance)}",
        f"Total income:     {_euro(account.total_income)}",
        f"Total expenses:   {_euro(account.total_expenses)}",
        f"Final balance:    {_euro(account.balance)}",
    ]

    lines.append(_heading("📅 Monthly summary"))
    lines.append(account.monthly_summary().to_string(float_format="{:,.2f}".format))

    lines.append(_heading("🏷️ Spending per category"))
    for category, amount in account.spending_by_category().items():
        lines.append(f"{category:<16} {amount:>12,.2f} €")

    lines.append(_heading("🔁 Recurring payments"))
    recurring = find_recurring(account)
    if recurring:
        lines += [str(payment) for payment in recurring]
    else:
        lines.append("None found.")

    lines.append(_heading(f"🔮 Balance forecast ({forecast_months} months)"))
    if len(month_end_balances(account)) >= 2:
        for month, value in forecast_balance(account, forecast_months).items():
            lines.append(f"{month}  {value:>12,.2f} €")
    else:
        lines.append("Need at least 2 months of data.")

    lines.append(_heading("💡 Tips"))
    lines += get_advice(account)

    return "\n".join(lines)

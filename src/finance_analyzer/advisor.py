"""Turn the numbers of an account into simple, written saving tips.

Every rule is a small function that looks at one thing. It returns a tip
(a string) if it has something to say, or None if everything is fine.
"""

from finance_analyzer.account import Account
from finance_analyzer.forecast import fit_trend, forecast_balance, month_end_balances
from finance_analyzer.recurring import find_recurring

# Rules of thumb used by financial advisors
GOOD_SAVINGS_RATE = 0.20  # save at least 20% of your income
MAX_HOUSING_SHARE = 0.30  # rent should be less than 30% of your income
EMERGENCY_MONTHS = 3  # keep at least 3 months of expenses as a safety net

# Categories where it is usually easiest to spend less
FLEXIBLE_CATEGORIES = ["Eating out", "Shopping"]


def savings_rate_tip(account: Account) -> str | None:
    if account.total_income <= 0:
        return None
    rate = (account.total_income + account.total_expenses) / account.total_income
    if rate < 0:
        return f"[Warning] You spend more than you earn: {-rate:.0%} over your income."
    if rate < GOOD_SAVINGS_RATE:
        return (
            f"[Warning] You save {rate:.0%} of your income. "
            f"Try to reach {GOOD_SAVINGS_RATE:.0%}."
        )
    return f"[Good]    Great job! You save {rate:.0%} of your income."


def housing_tip(account: Account) -> str | None:
    housing = account.spending_by_category().get("Housing", 0.0)
    if account.total_income <= 0 or housing == 0:
        return None
    share = housing / account.total_income
    if share > MAX_HOUSING_SHARE:
        return (
            f"[Warning] Housing takes {share:.0%} of your income "
            f"(recommended: under {MAX_HOUSING_SHARE:.0%})."
        )
    return None


def subscriptions_tip(account: Account) -> str | None:
    subscriptions = [
        payment
        for payment in find_recurring(account)
        if payment.amount < 0 and payment.description.lower() not in ("rent", "miete")
    ]
    if not subscriptions:
        return None
    yearly = -sum(payment.yearly_amount for payment in subscriptions)
    names = ", ".join(payment.description for payment in subscriptions)
    return (
        f"[Tip]     You have {len(subscriptions)} recurring payments ({names}) "
        f"costing {yearly:,.2f} € per year. Cancel the ones you don't use."
    )


def flexible_spending_tip(account: Account) -> str | None:
    spending = account.spending_by_category()
    months = len(account.monthly_summary())
    flexible = {c: spending[c] for c in FLEXIBLE_CATEGORIES if c in spending}
    if not flexible or months == 0:
        return None
    category = max(flexible, key=flexible.get)
    per_month = flexible[category] / months
    saving = flexible[category] / months * 12 * 0.25
    return (
        f"[Tip]     You spend {per_month:,.2f} € per month on {category}. "
        f"Cutting it by a quarter would save {saving:,.2f} € per year."
    )


def worst_month_tip(account: Account) -> str | None:
    summary = account.monthly_summary()
    if len(summary) < 2:
        return None
    worst = summary["net"].idxmin()
    return (
        f"[Info]    {worst} was your weakest month: you saved only "
        f"{summary.loc[worst, 'net']:,.2f} €. Check what happened there."
    )


def emergency_fund_tip(account: Account) -> str | None:
    months = len(account.monthly_summary())
    if months == 0:
        return None
    monthly_expenses = -account.total_expenses / months
    if monthly_expenses == 0:
        return None
    covered = account.balance / monthly_expenses
    if covered < EMERGENCY_MONTHS:
        return (
            f"[Warning] Your balance covers only {covered:.1f} months of expenses. "
            f"Aim for at least {EMERGENCY_MONTHS} months."
        )
    return f"[Good]    Your balance covers {covered:.1f} months of expenses. Nice safety net!"


def forecast_tip(account: Account, months: int = 6) -> str | None:
    history = month_end_balances(account)
    if len(history) < 2:
        return None
    slope, _ = fit_trend(history)
    future = forecast_balance(account, months)
    if slope < 0:
        return (
            f"[Warning] Your balance shrinks by {-slope:,.2f} € per month. "
            f"In {months} months it could be {future.iloc[-1]:,.2f} €."
        )
    return (
        f"[Info]    Your balance grows by {slope:,.2f} € per month. "
        f"In {months} months you could have {future.iloc[-1]:,.2f} €."
    )


RULES = [
    savings_rate_tip,
    housing_tip,
    subscriptions_tip,
    flexible_spending_tip,
    worst_month_tip,
    emergency_fund_tip,
]


def get_advice(account: Account, forecast_months: int = 6) -> list[str]:
    """Run every rule and collect the tips that have something to say."""
    tips = [rule(account) for rule in RULES]
    tips.append(forecast_tip(account, forecast_months))
    return [tip for tip in tips if tip is not None]

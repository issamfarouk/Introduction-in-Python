"""Predict the future account balance with a straight-line trend."""

import numpy as np
import pandas as pd

from finance_analyzer.account import Account


def month_end_balances(account: Account) -> pd.Series:
    """The balance on the last day of every month."""
    df = account.to_dataframe()
    return df.groupby("month")["balance"].last()


def fit_trend(balances: pd.Series) -> tuple[float, float]:
    """Fit a straight line through the balances.

    Returns (slope, intercept): the slope is how much the balance
    grows per month on average.
    """
    if len(balances) < 2:
        raise ValueError("Need at least 2 months of data to find a trend")
    months = np.arange(len(balances))
    slope, intercept = np.polyfit(months, balances.to_numpy(), deg=1)
    return float(slope), float(intercept)


def forecast_balance(account: Account, months: int = 6) -> pd.Series:
    """Predict the month-end balance for the next `months` months."""
    history = month_end_balances(account)
    slope, intercept = fit_trend(history)

    future_x = np.arange(len(history), len(history) + months)
    future_months = pd.period_range(history.index[-1] + 1, periods=months, freq="M")
    return pd.Series(slope * future_x + intercept, index=future_months, name="forecast")

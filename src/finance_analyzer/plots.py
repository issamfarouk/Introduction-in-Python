"""Draw charts of an account and save them as PNG files."""

from pathlib import Path

import matplotlib

# "Agg" saves charts to files without opening a window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from finance_analyzer.account import Account
from finance_analyzer.forecast import forecast_balance, month_end_balances

# Colors (one place, so every chart looks the same)
BLUE = "tab:blue"
ORANGE = "tab:orange"
GRAY = "dimgray"
LIGHT_GRAY = "lightgray"


def _style(ax: plt.Axes, title: str, title_pad: int = 14) -> None:
    """Give a chart the shared look: title, light grid, no box."""
    ax.set_title(title, loc="left", fontsize=14, pad=title_pad)
    ax.tick_params(colors=GRAY, labelsize=10, length=0)
    ax.grid(axis="y", color=LIGHT_GRAY, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRAY)


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_monthly(account: Account, path: Path) -> Path:
    """Bar chart: income and expenses side by side for every month."""
    summary = account.monthly_summary()
    months = [str(month) for month in summary.index]
    x = range(len(months))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        [i - width / 2 for i in x],
        summary["income"],
        width,
        color=BLUE,
        label="Income",
    )
    ax.bar(
        [i + width / 2 for i in x],
        -summary["expenses"],
        width,
        color=ORANGE,
        label="Expenses",
    )
    ax.set_xticks(list(x), months, rotation=45, ha="right")
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    _style(ax, "Income vs. expenses per month (€)", title_pad=30)
    # Put the legend above the chart so it never covers the bars
    ax.legend(frameon=False, ncols=2, loc="lower left", bbox_to_anchor=(0, 1.0))
    return _save(fig, path)


def plot_categories(account: Account, path: Path) -> Path:
    """Horizontal bar chart: where the money went, biggest category on top."""
    spending = account.spending_by_category().sort_values()

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(spending.index, spending.to_numpy(), color=BLUE, height=0.6)
    ax.bar_label(bars, labels=[f"{v:,.0f} €" for v in spending], padding=4)
    _style(ax, "Spending per category (€)")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=LIGHT_GRAY, linewidth=0.8)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(GRAY)
    ax.tick_params(axis="y", colors="black", labelsize=11)
    ax.margins(x=0.15)
    return _save(fig, path)


def plot_forecast(account: Account, path: Path, months: int = 6) -> Path:
    """Line chart: the real month-end balance, then the predicted balance."""
    history = month_end_balances(account)
    future = forecast_balance(account, months)

    # Start the forecast line at the last real point so the two lines connect
    forecast_x = [str(history.index[-1])] + [str(m) for m in future.index]
    forecast_y = [history.iloc[-1], *future.to_numpy()]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        [str(m) for m in history.index],
        history.to_numpy(),
        color=BLUE,
        linewidth=2,
        marker="o",
        markersize=5,
        label="Balance",
    )
    # Dashed line from the last real point, hollow markers only on predicted months
    ax.plot(
        forecast_x,
        forecast_y,
        color=BLUE,
        linewidth=2,
        linestyle="--",
        marker="o",
        markersize=5,
        markerfacecolor="white",
        markevery=slice(1, None),
        label="Forecast",
    )
    ax.annotate(
        f"{future.iloc[-1]:,.0f} €",
        (forecast_x[-1], forecast_y[-1]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    _style(ax, f"Month-end balance and {months}-month forecast (€)")
    ax.legend(frameon=False, loc="upper left")
    return _save(fig, path)


def save_all_plots(
    account: Account, folder: str | Path = "output", forecast_months: int = 6
) -> list[Path]:
    """Draw every chart into `folder` and return the file paths."""
    folder = Path(folder)
    return [
        plot_monthly(account, folder / "monthly_income_expenses.png"),
        plot_categories(account, folder / "spending_by_category.png"),
        plot_forecast(account, folder / "balance_forecast.png", forecast_months),
    ]

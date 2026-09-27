"""Draw charts of an account and save them as PNG files."""

from pathlib import Path

import matplotlib

# "Agg" draws straight into files, so no window is needed (works on any computer)
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from finance_analyzer.account import Account
from finance_analyzer.forecast import forecast_balance, month_end_balances

# Colors (one place, so every chart looks the same)
BLUE = "#2a78d6"
ORANGE = "#eb6834"
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"


def _style(ax: plt.Axes, title: str, ylabel: str = "") -> None:
    """Give a chart the shared look: light grid, no box, readable labels."""
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=14, color=TEXT, pad=14)
    ax.set_ylabel(ylabel, fontsize=11, color=TEXT_SECONDARY)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)
    return path


def plot_monthly(account: Account, path: Path) -> Path:
    """Bar chart: income and expenses side by side for every month."""
    summary = account.monthly_summary()
    months = [str(month) for month in summary.index]
    x = range(len(months))
    width = 0.38

    # A thin border in the background color leaves a small gap between bars
    gap = {"edgecolor": SURFACE, "linewidth": 1.5}

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
    ax.bar(
        [i - width / 2 for i in x],
        summary["income"],
        width,
        color=BLUE,
        label="Income",
        **gap,
    )
    ax.bar(
        [i + width / 2 for i in x],
        -summary["expenses"],
        width,
        color=ORANGE,
        label="Expenses",
        **gap,
    )
    ax.set_xticks(list(x), months, rotation=45, ha="right")
    _style(ax, "Income vs. expenses per month", "€")
    # Put the legend above the chart so it never covers the bars
    ax.legend(
        frameon=False,
        labelcolor=TEXT_SECONDARY,
        ncols=2,
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
    )
    ax.set_title(
        "Income vs. expenses per month", loc="left", fontsize=14, color=TEXT, pad=30
    )
    return _save(fig, path)


def plot_categories(account: Account, path: Path) -> Path:
    """Horizontal bar chart: where the money went, biggest category on top."""
    spending = account.spending_by_category().sort_values()

    fig, ax = plt.subplots(figsize=(9, 5), facecolor=SURFACE)
    bars = ax.barh(spending.index, spending.to_numpy(), color=BLUE, height=0.6)
    ax.bar_label(
        bars,
        labels=[f"{v:,.0f} €" for v in spending],
        padding=4,
        color=TEXT_SECONDARY,
        fontsize=10,
    )
    _style(ax, "Spending per category")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(BASELINE)
    ax.tick_params(axis="y", colors=TEXT_SECONDARY, labelsize=11)
    ax.margins(x=0.15)
    return _save(fig, path)


def plot_forecast(account: Account, path: Path, months: int = 6) -> Path:
    """Line chart: the real month-end balance, then the predicted balance."""
    history = month_end_balances(account)
    future = forecast_balance(account, months)

    # Start the forecast line at the last real point so the two lines connect
    forecast_x = [str(history.index[-1])] + [str(m) for m in future.index]
    forecast_y = [history.iloc[-1], *future.to_numpy()]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
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
        markerfacecolor=SURFACE,
        markevery=slice(1, None),
        label="Forecast",
    )
    ax.annotate(
        f"{future.iloc[-1]:,.0f} €",
        (forecast_x[-1], forecast_y[-1]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        color=TEXT_SECONDARY,
        fontsize=10,
    )
    ax.tick_params(axis="x", rotation=45)
    _style(ax, f"Month-end balance and {months}-month forecast", "€")
    ax.legend(frameon=False, labelcolor=TEXT_SECONDARY, loc="upper left")
    return _save(fig, path)


def save_all_plots(account: Account, folder: str | Path = "output") -> list[Path]:
    """Draw every chart into `folder` and return the file paths."""
    folder = Path(folder)
    return [
        plot_monthly(account, folder / "monthly_income_expenses.png"),
        plot_categories(account, folder / "spending_by_category.png"),
        plot_forecast(account, folder / "balance_forecast.png"),
    ]

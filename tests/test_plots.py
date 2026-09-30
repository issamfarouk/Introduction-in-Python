from pathlib import Path

import matplotlib.pyplot as plt

from finance_analyzer import Account, save_all_plots
from finance_analyzer.plots import plot_categories

DATA = Path(__file__).parent.parent / "data"


def test_all_charts_are_saved(tmp_path):
    account = Account.from_csv(DATA / "sample_transactions.csv")
    paths = save_all_plots(account, tmp_path)

    assert len(paths) == 3
    for path in paths:
        assert path.exists()


def test_category_chart_shows_names(tmp_path, monkeypatch):
    # Keep the chart open so we can look at its labels
    monkeypatch.setattr(plt, "close", lambda fig: None)
    account = Account.from_csv(DATA / "sample_transactions.csv")
    plot_categories(account, tmp_path / "categories.png")

    labels = [label.get_text() for label in plt.gca().get_yticklabels()]
    assert "Housing" in labels
    plt.close("all")

# Finance Analyzer

A command-line tool that reads your bank statement (CSV), shows where your
money goes, detects recurring payments like subscriptions, forecasts your
balance, and gives you written tips on how to save more.

It works with a simple international CSV format and with the format used by
German banks, and it ships with a generator for realistic sample data, so you
can try it without using your own bank data.

## Features

- **Monthly summary** of income, expenses, and savings
- **Automatic categories** (Groceries, Housing, Subscriptions, ...) based on the description
- **Recurring payment detection**: finds subscriptions, rent, and salary on its own,
  without being told their names
- **Balance forecast** for the coming months using a linear trend
- **Saving tips** based on common rules of thumb (e.g. save 20% of your income,
  keep rent under 30%)
- **Charts** saved as PNG files
- **Sample data generator** for a full year of realistic transactions

## Installation

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/issamfarouk/finance-analyzer.git
cd finance-analyzer
uv sync
```

Alternatively, install it in editable mode into an existing environment:

```bash
uv pip install -e .
```

## Usage

Show all commands:

```bash
uv run -m finance_analyzer --help
```

### Analyze a bank statement

```bash
uv run -m finance_analyzer report data/sample_transactions.csv --balance 1000
```

| Option | Meaning | Default |
|---|---|---|
| `file` | the bank statement CSV file | (required) |
| `--balance` | account balance before the first transaction | `0` |
| `--months` | how many months to forecast | `6` |
| `--output` | folder for the report and charts | `output` |

The report is printed to the terminal and also saved as `output/report.txt`.

### Create sample data

```bash
uv run -m finance_analyzer generate
```

| Option | Meaning | Default |
|---|---|---|
| `--output` | where to save the CSV file | `data/sample_transactions.csv` |
| `--months` | how many months of transactions | `12` |
| `--seed` | random seed (the same seed always gives the same data) | `42` |

## Example output

Running the `report` command on the included sample data prints
([full report](output/report.txt)):

```text
Tips
----
[Good]    Great job! You save 21% of your income.
[Warning] Housing takes 36% of your income (recommended: under 30%).
[Tip]     You have 5 recurring payments (Deutschlandticket, FitX Gym, Vodafone Mobile, Netflix, Spotify) costing 1,523.52 € per year. Cancel the ones you don't use.
[Tip]     You spend 250.19 € per month on Shopping. Cutting it by a quarter would save 750.58 € per year.
[Info]    2026-03 was your weakest month: you saved only 243.64 €. Check what happened there.
[Good]    Your balance covers 3.8 months of expenses. Nice safety net!
[Info]    Your balance grows by 429.58 € per month. In 6 months you could have 8,800.67 €.
```

and saves these charts to `output/`:

![Income vs. expenses per month](output/monthly_income_expenses.png)

![Spending per category](output/spending_by_category.png)

![Month-end balance and forecast](output/balance_forecast.png)

## Input formats

The format is detected automatically from the first line of the file.

**Generic CSV** (see [`data/sample_transactions.csv`](data/sample_transactions.csv)):

```text
Date,Description,Amount
2025-10-01,Rent,-750.00
2025-10-25,Salary,2100.00
```

**German bank CSV** (see [`data/example_german_bank.csv`](data/example_german_bank.csv)):

```text
Buchungstag;Verwendungszweck;Betrag
01.10.2025;Miete;-750,00
25.10.2025;Gehalt;2.100,00
```

Negative amounts are money going out, positive amounts are money coming in.

## Using it as a library

The most important parts are available directly from the package:

```python
from finance_analyzer import Account, find_recurring, forecast_balance, get_advice

account = Account.from_csv("data/sample_transactions.csv", starting_balance=1000)

print(account.balance)
print(account.monthly_summary())
print(account.spending_by_category())

for payment in find_recurring(account):
    print(payment)

print(forecast_balance(account, months=12))

for tip in get_advice(account):
    print(tip)
```

## How it works

| Module | What it does |
|---|---|
| `transaction.py` | `Transaction` class: one line of a bank statement |
| `importers.py` | `BankImporter` abstract base class with one subclass per file format |
| `account.py` | `Account` class: balance, monthly summary, and spending per category using pandas |
| `categorizer.py` | assigns a category by looking for keywords in the description |
| `recurring.py` | finds payments that repeat with the same amount at regular intervals |
| `forecast.py` | fits a straight line through the month-end balances with NumPy and extends it |
| `advisor.py` | a list of small rules, each returning a tip or nothing |
| `plots.py` | draws the charts with matplotlib |
| `report.py` | combines everything into one text report |
| `generator.py` | creates realistic fake transactions |
| `__main__.py` | the command-line interface |

**Recurring payments:** transactions are grouped by description. A group counts
as recurring if it appears at least 3 times, its amount never differs by more
than 5% from the average, and the median gap between dates matches a weekly,
monthly, or yearly rhythm.

**Forecast:** the forecast assumes your habits stay the same. It cannot know
about future changes like a new job or a large one-time purchase.

## Development

Check and format the code with [ruff](https://docs.astral.sh/ruff/):

```bash
uv run ruff check src
uv run ruff format src
```

## Author

**Mohamed Gomaa** ([@issamfarouk](https://github.com/issamfarouk))<br>
mohamed.gomaa@tu-dortmund.de

Final project for the course *Introduction in Python* at TU Dortmund.

"""Command-line interface.

Run `uv run -m finance_analyzer --help` to see all commands.
"""

import argparse
import sys
from pathlib import Path

from finance_analyzer.account import Account
from finance_analyzer.generator import generate_transactions, save_to_csv
from finance_analyzer.importers import StatementError
from finance_analyzer.plots import save_all_plots
from finance_analyzer.report import build_report


def run_report(args: argparse.Namespace) -> None:
    account = Account.from_csv(
        args.file,
        starting_balance=args.balance,
        date_column=args.date_column,
        description_column=args.description_column,
        amount_column=args.amount_column,
    )
    report = build_report(account, name=args.file.name, forecast_months=args.months)
    print(report)

    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "report.txt"
    report_path.write_text(report + "\n", encoding="utf-8")

    print("\nSaved files:")
    print(f"   {report_path}")
    if len(account) > 0 and len(account.monthly_summary()) >= 2:
        for path in save_all_plots(account, args.output, args.months):
            print(f"   {path}")


def run_generate(args: argparse.Namespace) -> None:
    transactions = generate_transactions(months=args.months, seed=args.seed)
    save_to_csv(transactions, args.output)
    print(f"Saved {len(transactions)} transactions to {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finance_analyzer",
        description="Analyze bank transactions, find recurring payments, "
        "forecast your balance, and get saving tips.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    report = commands.add_parser("report", help="analyze a bank statement CSV file")
    report.add_argument("file", type=Path, help="bank statement CSV file")
    report.add_argument(
        "--balance",
        type=float,
        help="account balance before the first transaction "
        "(default: taken from the file if it has a balance column, otherwise 0)",
    )
    # Only needed when the columns of the file cannot be found automatically
    report.add_argument("--date-column", help="name of the column with the dates")
    report.add_argument("--amount-column", help="name of the column with the amounts")
    report.add_argument(
        "--description-column", help="name of the column with the descriptions"
    )
    report.add_argument(
        "--months",
        type=int,
        default=6,
        help="how many months to forecast (default: 6)",
    )
    report.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="folder for the report and charts (default: output)",
    )
    report.set_defaults(func=run_report)

    generate = commands.add_parser(
        "generate", help="create a CSV file with fake transactions"
    )
    generate.add_argument(
        "--output",
        type=Path,
        default=Path("data/sample_transactions.csv"),
        help="where to save the file (default: data/sample_transactions.csv)",
    )
    generate.add_argument(
        "--months",
        type=int,
        default=12,
        help="how many months of data (default: 12)",
    )
    generate.add_argument(
        "--seed",
        type=int,
        default=42,
        help="random seed; the same seed gives the same data (default: 42)",
    )
    generate.set_defaults(func=run_generate)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.months < 1:
        print("Error: --months must be 1 or more", file=sys.stderr)
        sys.exit(1)
    try:
        args.func(args)
    except (FileNotFoundError, StatementError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

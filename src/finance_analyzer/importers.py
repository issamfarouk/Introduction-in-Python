"""Read bank statement files (CSV) into Transaction objects.

Every bank exports its statements a little differently. Each importer class
knows how to read one format, and they all share the same loading logic
from the BankImporter base class.
"""

import csv
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from finance_analyzer.transaction import Transaction


class StatementError(Exception):
    """Raised when a bank statement file cannot be read."""


class BankImporter(ABC):
    """Base class for all importers. Subclasses must implement parse_row.

    Rows with a missing date or amount are skipped instead of stopping the
    whole import. The reason for every skipped row is kept in `self.skipped`.
    """

    delimiter = ","
    MISSING_DESCRIPTION = "(no description)"

    def __init__(self) -> None:
        self.skipped: list[str] = []

    @abstractmethod
    def parse_row(self, row: dict[str, str]) -> Transaction:
        """Turn one row of the CSV file into a Transaction."""

    @staticmethod
    def required(row: dict[str, str], column: str) -> str:
        """Return the value of `column`, or raise ValueError if it is empty."""
        value = row[column]
        if not value:
            raise ValueError(f"missing {column}")
        return value

    def load(self, path: str | Path) -> list[Transaction]:
        """Read every row of the file and return the transactions sorted by date."""
        path = Path(path)
        self.skipped = []
        transactions = []
        # "utf-8-sig" also reads CSV files saved by Excel
        with open(path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            for row in reader:
                # Remove extra spaces; missing columns become empty strings
                row = {key: (value or "").strip() for key, value in row.items() if key}
                if not any(row.values()):
                    continue
                try:
                    transactions.append(self.parse_row(row))
                except (KeyError, ValueError) as error:
                    self.skipped.append(f"line {reader.line_num}: {error}")

        if not transactions and self.skipped:
            raise StatementError(
                f"{path.name}: no valid transactions ({self.skipped[0]})"
            )
        return sorted(transactions)


class GenericCsvImporter(BankImporter):
    """Simple format, for example: 2025-10-01,Rent,-750.00"""

    def parse_row(self, row: dict[str, str]) -> Transaction:
        return Transaction(
            date.fromisoformat(self.required(row, "Date")),
            row["Description"] or self.MISSING_DESCRIPTION,
            float(self.required(row, "Amount")),
        )


class GermanBankImporter(BankImporter):
    """German format, for example: 01.10.2025;Miete;-1.234,56"""

    delimiter = ";"

    def parse_row(self, row: dict[str, str]) -> Transaction:
        day, month, year = self.required(row, "Buchungstag").split(".")
        # Some banks write the year with two digits: 01.10.25
        if len(year) == 2:
            year = "20" + year
        # German numbers: "." separates thousands, "," is the decimal point
        amount = self.required(row, "Betrag").replace(".", "").replace(",", ".")
        return Transaction(
            date(int(year), int(month), int(day)),
            row["Verwendungszweck"] or self.MISSING_DESCRIPTION,
            float(amount),
        )


def detect_importer(path: str | Path) -> BankImporter:
    """Look at the first line of the file and pick the right importer."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    if not path.is_file():
        raise StatementError(f"{path} is a folder, not a CSV file")

    with open(path, encoding="utf-8-sig") as file:
        header = file.readline()

    if "Buchungstag" in header:
        return GermanBankImporter()
    if "Date" in header:
        return GenericCsvImporter()
    raise StatementError(f"{path.name}: unknown file format (header: {header.strip()})")


def load_transactions(path: str | Path) -> list[Transaction]:
    """Load a bank statement, detecting its format automatically."""
    return detect_importer(path).load(path)

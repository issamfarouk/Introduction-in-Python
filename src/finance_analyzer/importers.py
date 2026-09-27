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
    """Base class for all importers. Subclasses must implement parse_row."""

    delimiter = ","

    @abstractmethod
    def parse_row(self, row: dict[str, str]) -> Transaction:
        """Turn one row of the CSV file into a Transaction."""

    def load(self, path: str | Path) -> list[Transaction]:
        """Read every row of the file and return the transactions sorted by date."""
        path = Path(path)
        transactions = []
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            # Line 1 is the header, so the first data row is line 2
            for line_number, row in enumerate(reader, start=2):
                try:
                    transactions.append(self.parse_row(row))
                except (KeyError, ValueError) as error:
                    raise StatementError(
                        f"{path.name}, line {line_number}: {error}"
                    ) from error
        return sorted(transactions)


class GenericCsvImporter(BankImporter):
    """Format: Date,Description,Amount  e.g.  2025-10-01,Rent,-750.00"""

    def parse_row(self, row: dict[str, str]) -> Transaction:
        return Transaction(
            date.fromisoformat(row["Date"]),
            row["Description"],
            float(row["Amount"]),
        )


class GermanBankImporter(BankImporter):
    """Format used by German banks:  01.10.2025;Miete;-1.234,56"""

    delimiter = ";"

    def parse_row(self, row: dict[str, str]) -> Transaction:
        day, month, year = row["Buchungstag"].split(".")
        # German numbers: "." separates thousands, "," is the decimal point
        amount = row["Betrag"].replace(".", "").replace(",", ".")
        return Transaction(
            date(int(year), int(month), int(day)),
            row["Verwendungszweck"],
            float(amount),
        )


def detect_importer(path: str | Path) -> BankImporter:
    """Look at the first line of the file and pick the right importer."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    with open(path, encoding="utf-8") as file:
        header = file.readline()

    if "Buchungstag" in header:
        return GermanBankImporter()
    if "Date" in header:
        return GenericCsvImporter()
    raise StatementError(f"{path.name}: unknown file format (header: {header.strip()})")


def load_transactions(path: str | Path) -> list[Transaction]:
    """Load a bank statement, detecting its format automatically."""
    return detect_importer(path).load(path)

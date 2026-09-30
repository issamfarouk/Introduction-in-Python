"""Read bank statement files (CSV) into Transaction objects.

Banks export their statements in different ways: other column names,
separators, date formats and number formats. CsvImporter looks at the file
and works these things out by itself. A bank that also has rules of its own
gets a small subclass (RevolutImporter).
"""

import csv
from datetime import date
from pathlib import Path

from finance_analyzer.categorizer import categorize
from finance_analyzer.transaction import Transaction

# Words that show what a column holds (lowercase, English and German).
# Earlier words win, so the more exact ones come first.
DATE_WORDS = ["completed date", "booking date", "buchungstag", "date", "datum"]
AMOUNT_WORDS = ["amount", "betrag", "umsatz"]
DESCRIPTION_WORDS = [
    "description",
    "verwendungszweck",
    "partner name",
    "payee",
    "reference",
    "text",
]
BALANCE_WORDS = ["balance", "saldo", "kontostand"]


class StatementError(Exception):
    """Raised when a bank statement file cannot be read."""


def parse_date(text: str) -> date:
    """Read a date like 2025-10-01, 01.10.2025, 01.10.25 or 01/10/2025.

    A time after the date ("2025-10-01 09:15:04") is ignored.
    """
    text = text.split(" ")[0]
    try:
        if "-" in text:
            return date.fromisoformat(text)
        day, month, year = text.replace("/", ".").split(".")
        if len(year) == 2:
            year = "20" + year
        return date(int(year), int(month), int(day))
    except ValueError:
        raise ValueError(f"unknown date format: {text}") from None


def parse_amount(text: str) -> float:
    """Read a number written the English (1,234.56) or German (1.234,56) way."""
    text = text.replace("€", "").replace(" ", "")
    if "," in text and "." in text:
        # The separator that comes last is the decimal point
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    return float(text)


def looks_like(parse, text: str) -> bool:
    """True if `parse` (parse_date or parse_amount) can read the text."""
    try:
        parse(text)
    except ValueError:
        return False
    return True


def find_column(columns: list[str], words: list[str]) -> str | None:
    """Return the first column whose name contains one of the words."""
    for word in words:
        for column in columns:
            if word in column.lower():
                return column
    return None


class CsvImporter:
    """Reads a bank statement and finds the date, amount and description columns.

    Rows with a missing date or amount are skipped, and the reason is kept
    in `self.skipped`. If the file has a balance column, `self.starting_balance`
    is the balance before the first transaction.
    """

    MISSING_DESCRIPTION = "(no description)"

    def __init__(
        self,
        date_column: str | None = None,
        description_column: str | None = None,
        amount_column: str | None = None,
    ) -> None:
        self.date_column = date_column
        self.description_column = description_column
        self.amount_column = amount_column
        self.balance_column: str | None = None
        self.skipped: list[str] = []
        self.starting_balance: float | None = None

    @staticmethod
    def required(row: dict[str, str], column: str) -> str:
        """Return the value of `column`, or raise ValueError if it is empty."""
        value = row[column]
        if not value:
            raise ValueError(f"missing {column}")
        return value

    def parse_row(self, row: dict[str, str]) -> Transaction:
        """Turn one row of the CSV file into a Transaction."""
        return Transaction(
            parse_date(self.required(row, self.date_column)),
            row.get(self.description_column) or self.MISSING_DESCRIPTION,
            parse_amount(self.required(row, self.amount_column)),
        )

    def find_columns(self, columns: list[str], first_row: dict[str, str]) -> None:
        """Decide which column is the date, the amount, and the description."""
        for column in (self.date_column, self.description_column, self.amount_column):
            if column is not None and column not in columns:
                raise StatementError(f"no column named {column!r} in {columns}")

        self.balance_column = find_column(columns, BALANCE_WORDS)

        # 1. By name
        if self.date_column is None:
            self.date_column = find_column(columns, DATE_WORDS)
        if self.amount_column is None:
            self.amount_column = find_column(columns, AMOUNT_WORDS)
        if self.description_column is None:
            self.description_column = find_column(columns, DESCRIPTION_WORDS)

        # 2. By content, for columns with unknown names
        if self.date_column is None:
            dates = [c for c in columns if looks_like(parse_date, first_row[c])]
            if dates:
                self.date_column = dates[0]
        if self.amount_column is None:
            numbers = [
                c
                for c in columns
                if c not in (self.date_column, self.balance_column)
                and looks_like(parse_amount, first_row[c])
            ]
            # With two or more number columns we cannot know which is the amount
            if len(numbers) == 1:
                self.amount_column = numbers[0]
        if self.description_column is None:
            used = (self.date_column, self.amount_column, self.balance_column)
            texts = [
                c
                for c in columns
                if c not in used
                and first_row[c]
                and not looks_like(parse_amount, first_row[c])
                and not looks_like(parse_date, first_row[c])
            ]
            if texts:
                self.description_column = texts[0]

        if self.date_column is None:
            raise StatementError(
                f"could not find the date column in {columns} (use --date-column)"
            )
        if self.amount_column is None:
            raise StatementError(
                f"could not find the amount column in {columns} (use --amount-column)"
            )

    def load(self, path: str | Path) -> list[Transaction]:
        """Read every row of the file and return the transactions sorted by date."""
        path = Path(path)
        self.skipped = []
        self.starting_balance = None

        # "utf-8-sig" also reads CSV files saved by Excel
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if not lines:
            raise StatementError(f"{path.name}: the file is empty")
        # The separator is the character that appears most often in the header
        delimiter = max(",;\t", key=lines[0].count)
        reader = csv.DictReader(lines, delimiter=delimiter)

        # Remove extra spaces; missing columns become empty strings
        rows = []
        for row in reader:
            row = {key: (value or "").strip() for key, value in row.items() if key}
            if any(row.values()):
                rows.append((reader.line_num, row))
        if not rows:
            return []

        try:
            self.find_columns(list(rows[0][1]), rows[0][1])
        except StatementError as error:
            raise StatementError(f"{path.name}: {error}") from error

        transactions = []
        balances = []  # the balance before each transaction, if the file has one
        for line_number, row in rows:
            try:
                transaction = self.parse_row(row)
            except KeyError as error:
                self.skipped.append(f"line {line_number}: no column {error}")
                continue
            except ValueError as error:
                self.skipped.append(f"line {line_number}: {error}")
                continue
            transactions.append(transaction)
            if self.balance_column and row[self.balance_column]:
                balance_after = parse_amount(row[self.balance_column])
                balances.append(balance_after - transaction.amount)

        if not transactions:
            raise StatementError(
                f"{path.name}: no valid transactions ({self.skipped[0]})"
            )
        if len(balances) == len(transactions):
            # The first transaction is on the first line,
            # or on the last line if the newest comes first
            oldest_first = transactions[0].date <= transactions[-1].date
            self.starting_balance = balances[0] if oldest_first else balances[-1]
        return sorted(transactions)


class RevolutImporter(CsvImporter):
    """Revolut statements also have a State, a Fee and a Type column.

    Cancelled payments are skipped and the fee is subtracted from the amount.
    A transfer that no keyword recognizes is put in the "Transfers" category.
    """

    def parse_row(self, row: dict[str, str]) -> Transaction:
        """Read the row like CsvImporter does, then apply the Revolut rules."""
        if row["State"] != "COMPLETED":
            raise ValueError(f"payment not completed ({row['State']})")
        transaction = super().parse_row(row)
        transaction.amount -= parse_amount(row["Fee"] or "0")

        category = categorize(transaction.description, transaction.amount)
        if row["Type"] == "Transfer" and category in ("Other", "Other income"):
            transaction.category = "Transfers"
        return transaction


def detect_importer(
    path: str | Path,
    date_column: str | None = None,
    description_column: str | None = None,
    amount_column: str | None = None,
) -> CsvImporter:
    """Look at the first line of the file and pick the right importer."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    if not path.is_file():
        raise StatementError(f"{path} is a folder, not a CSV file")

    with open(path, encoding="utf-8-sig") as file:
        columns = file.readline().strip().split(",")

    if "State" in columns and "Fee" in columns and "Type" in columns:
        return RevolutImporter(date_column, description_column, amount_column)
    return CsvImporter(date_column, description_column, amount_column)


def load_transactions(path: str | Path) -> list[Transaction]:
    """Load a bank statement, detecting its format automatically."""
    return detect_importer(path).load(path)

from datetime import date
from pathlib import Path

import pytest

from finance_analyzer.importers import (
    GermanBankImporter,
    StatementError,
    detect_importer,
    load_transactions,
)

DATA = Path(__file__).parent.parent / "data"


def test_load_sample_file():
    transactions = load_transactions(DATA / "sample_transactions.csv")

    assert len(transactions) == 379
    assert transactions[0].date == date(2025, 10, 1)


def test_load_german_file():
    transactions = load_transactions(DATA / "example_german_bank.csv")
    salary = transactions[-1]

    assert isinstance(
        detect_importer(DATA / "example_german_bank.csv"), GermanBankImporter
    )
    assert salary.description == "Gehalt"
    assert salary.amount == 2100.0  # written as "2.100,00" in the file


def test_german_two_digit_year(tmp_path):
    file = tmp_path / "bank.csv"
    file.write_text("Buchungstag;Verwendungszweck;Betrag\n01.10.25;Miete;-750,00\n")

    assert load_transactions(file)[0].date == date(2025, 10, 1)


def test_bad_rows_are_skipped(tmp_path):
    file = tmp_path / "messy.csv"
    file.write_text(
        "Date,Description,Amount\n"
        "2025-10-01,Rent,-750.00\n"
        "2025-10-02,,-4.50\n"
        "2025-10-03,Lidl,\n"
        ",Netflix,-12.99\n"
    )
    importer = detect_importer(file)
    transactions = importer.load(file)

    assert len(transactions) == 2
    assert transactions[1].description == "(no description)"
    assert importer.skipped == ["line 4: missing Amount", "line 5: missing Date"]


def test_folder_is_rejected():
    with pytest.raises(StatementError):
        load_transactions(DATA)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_transactions(DATA / "does_not_exist.csv")

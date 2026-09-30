from datetime import date
from pathlib import Path

import pytest

from finance_analyzer.importers import (
    CsvImporter,
    RevolutImporter,
    StatementError,
    detect_importer,
    load_transactions,
    parse_amount,
    parse_date,
)

DATA = Path(__file__).parent.parent / "data"


def test_parse_amount_english_and_german():
    assert parse_amount("1,234.56") == 1234.56
    assert parse_amount("1.234,56") == 1234.56
    assert parse_amount("-750,00") == -750.0
    assert parse_amount("12.99") == 12.99


def test_parse_date_formats():
    expected = date(2025, 10, 1)

    assert parse_date("2025-10-01") == expected
    assert parse_date("2025-10-01 09:15:04") == expected
    assert parse_date("01.10.2025") == expected
    assert parse_date("01.10.25") == expected
    assert parse_date("01/10/2025") == expected


def test_load_sample_file():
    transactions = load_transactions(DATA / "sample_transactions.csv")

    assert len(transactions) == 379
    assert transactions[0].date == date(2025, 10, 1)


def test_load_german_file():
    transactions = load_transactions(DATA / "example_german_bank.csv")
    salary = transactions[-1]

    assert salary.date == date(2025, 10, 25)
    assert salary.description == "Gehalt"
    assert salary.amount == 2100.0  # written as "2.100,00" in the file


def test_load_revolut_file():
    file = DATA / "example_revolut.csv"
    importer = detect_importer(file)
    transactions = importer.load(file)

    assert isinstance(importer, RevolutImporter)
    assert len(transactions) == 3
    # The fee of 0.50 is added to the 40.00 that were sent
    assert transactions[-1].amount == -40.50
    # The cancelled Amazon payment is not counted
    assert importer.skipped == ["line 4: payment not completed (REVERTED)"]
    # 600.00 after a top-up of 500.00 means the account started with 100.00
    assert importer.starting_balance == 100.0


def test_quoted_columns_with_longer_names(tmp_path):
    file = tmp_path / "bank.csv"
    file.write_text(
        '"Booking Date","Value Date","Partner Name","Type","Amount (EUR)"\n'
        '"2025-10-01","2025-10-02","Lidl","Card","-23.45"\n'
    )
    transaction = load_transactions(file)[0]

    assert transaction.date == date(2025, 10, 1)
    assert transaction.description == "Lidl"
    assert transaction.amount == -23.45


def test_unknown_column_names_are_found_by_their_content(tmp_path):
    file = tmp_path / "banco.csv"
    file.write_text("Fecha;Concepto;Importe\n01/10/2025;Alquiler;-750,00\n")
    transaction = load_transactions(file)[0]

    assert transaction.date == date(2025, 10, 1)
    assert transaction.description == "Alquiler"
    assert transaction.amount == -750.0


def test_two_number_columns_need_a_column_name(tmp_path):
    file = tmp_path / "unclear.csv"
    file.write_text("Day,What,A,B\n2025-10-01,Rent,-750.00,1250.00\n")

    with pytest.raises(StatementError):
        load_transactions(file)

    importer = CsvImporter(amount_column="A")
    assert importer.load(file)[0].amount == -750.0


def test_starting_balance_when_newest_is_first(tmp_path):
    file = tmp_path / "bank.csv"
    file.write_text(
        "Date,Description,Amount,Balance\n"
        "2025-10-02,Lidl,-20.00,180.00\n"
        "2025-10-01,Salary,100.00,200.00\n"
    )
    importer = detect_importer(file)
    importer.load(file)

    assert importer.starting_balance == 100.0


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

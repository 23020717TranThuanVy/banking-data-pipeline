"""Unit checks for reading the mock CSV file."""

from pathlib import Path

import pytest

from banking_pipeline.extract import extract_transactions


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def test_extract_reads_all_sample_rows_and_preserves_empty_fields() -> None:
    rows = extract_transactions()

    assert len(rows) == 15
    assert rows[0]["transaction_id"] == "TXN0001"
    assert rows[9]["transaction_id"] == ""


def test_extract_reports_missing_required_columns() -> None:
    csv_path = FIXTURE_DIR / "incomplete.csv"

    with pytest.raises(ValueError):
        extract_transactions(csv_path)

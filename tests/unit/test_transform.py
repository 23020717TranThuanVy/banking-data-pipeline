"""Unit checks for transaction normalization and data quality rules."""

from datetime import datetime
from decimal import Decimal

from banking_pipeline.extract import extract_transactions
from banking_pipeline.transform import transform_transactions


def make_valid_row(**overrides: str) -> dict[str, str]:
    row = {
        "transaction_id": "TXN1000",
        "account_id": "ACC1000",
        "transaction_date": "2026-10-01T10:00:00",
        "transaction_type": "deposit",
        "amount": "100.25",
        "currency": "VND",
        "status": "completed",
        "counterparty_account_id": "",
    }
    row.update(overrides)
    return row


def test_transform_normalizes_values_and_parses_precise_types() -> None:
    row = make_valid_row(
        transaction_id=" txn1000 ",
        account_id=" acc1000 ",
        transaction_type=" DEPOSIT ",
        currency="vnd",
        status=" COMPLETED ",
    )

    result = transform_transactions([row])

    assert len(result.valid_transactions) == 1
    assert result.rejected_transactions == []
    transaction = result.valid_transactions[0]
    assert transaction.transaction_id == "TXN1000"
    assert transaction.account_id == "ACC1000"
    assert transaction.transaction_type == "deposit"
    assert transaction.currency == "VND"
    assert transaction.status == "completed"
    assert transaction.transaction_date == datetime(2026, 10, 1, 10, 0)
    assert transaction.amount == Decimal("100.25")
    assert transaction.counterparty_account_id is None


def test_transform_collects_rejection_reasons_and_keeps_original_row() -> None:
    row = make_valid_row(
        transaction_id="",
        account_id="",
        transaction_date="not-a-date",
        transaction_type="transfer",
        amount="0",
        status="unknown",
    )

    result = transform_transactions([row])

    assert result.valid_transactions == []
    rejected = result.rejected_transactions[0]
    assert rejected.row_number == 1
    assert rejected.raw_data == row
    assert set(rejected.reasons) == {
        "missing_transaction_id",
        "missing_account_id",
        "invalid_transaction_date",
        "non_positive_amount",
        "unsupported_status",
        "missing_counterparty_account_id",
    }


def test_transform_keeps_first_occurrence_and_rejects_duplicate_id() -> None:
    first = make_valid_row()
    duplicate = make_valid_row(amount="250.00")

    result = transform_transactions([first, duplicate])

    assert [item.transaction_id for item in result.valid_transactions] == ["TXN1000"]
    assert len(result.rejected_transactions) == 1
    assert result.rejected_transactions[0].row_number == 2
    assert result.rejected_transactions[0].reasons == ["duplicate_transaction_id"]


def test_sample_csv_has_expected_valid_and_rejected_rows() -> None:
    result = transform_transactions(extract_transactions())

    assert len(result.valid_transactions) == 9
    assert len(result.rejected_transactions) == 6
    assert [item.reasons[0] for item in result.rejected_transactions] == [
        "missing_transaction_id",
        "invalid_transaction_date",
        "non_positive_amount",
        "missing_account_id",
        "unsupported_transaction_type",
        "duplicate_transaction_id",
    ]

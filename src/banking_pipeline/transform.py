"""Normalize transactions and separate valid rows from rejected rows."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Iterable, Mapping


ALLOWED_TRANSACTION_TYPES = {"deposit", "withdrawal", "transfer", "payment"}
ALLOWED_STATUSES = {"completed", "pending", "failed"}
CURRENCY_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True)
class Transaction:
    """A valid transaction with normalized values and Python data types."""

    transaction_id: str
    account_id: str
    transaction_date: datetime
    transaction_type: str
    amount: Decimal
    currency: str
    status: str
    counterparty_account_id: str | None


@dataclass(frozen=True)
class RejectedTransaction:
    """A rejected source row, its data, row number, and reason codes."""

    row_number: int
    raw_data: dict[str, str | None]
    reasons: list[str]


@dataclass
class TransformResult:
    """Valid and rejected records produced from one input batch."""

    valid_transactions: list[Transaction]
    rejected_transactions: list[RejectedTransaction]


def _clean(value: str | None) -> str:
    """Trim whitespace and represent empty or absent values as an empty string."""
    return (value or "").strip()


def transform_transactions(
    rows: Iterable[Mapping[str, str | None]],
) -> TransformResult:
    """Normalize extracted rows and collect every applicable rejection code.

    Row numbers start at 1 for the first data row, excluding the CSV header.
    The first occurrence of a transaction ID in a batch reserves that ID;
    later occurrences are rejected as duplicates.
    """
    valid_transactions: list[Transaction] = []
    rejected_transactions: list[RejectedTransaction] = []
    seen_transaction_ids: set[str] = set()

    for row_number, row in enumerate(rows, start=1):
        raw_data = dict(row)
        values = {key: _clean(value) for key, value in row.items()}
        reasons: list[str] = []

        transaction_id = values.get("transaction_id", "").upper()
        account_id = values.get("account_id", "").upper()
        transaction_date_text = values.get("transaction_date", "")
        transaction_type = values.get("transaction_type", "").lower()
        amount_text = values.get("amount", "")
        currency = values.get("currency", "").upper()
        status = values.get("status", "").lower()
        counterparty_id = values.get("counterparty_account_id", "").upper() or None

        if not transaction_id:
            reasons.append("missing_transaction_id")
        elif transaction_id in seen_transaction_ids:
            reasons.append("duplicate_transaction_id")
        else:
            seen_transaction_ids.add(transaction_id)

        if not account_id:
            reasons.append("missing_account_id")

        transaction_date: datetime | None = None
        try:
            if "T" not in transaction_date_text.upper():
                raise ValueError("timestamp is missing its time component")
            transaction_date = datetime.fromisoformat(transaction_date_text)
        except ValueError:
            reasons.append("invalid_transaction_date")

        amount: Decimal | None = None
        try:
            amount = Decimal(amount_text)
            if not amount.is_finite():
                reasons.append("amount_not_finite")
                amount = None
            elif amount <= 0:
                reasons.append("non_positive_amount")
                amount = None
        except InvalidOperation:
            reasons.append("amount_not_numeric")

        if transaction_type not in ALLOWED_TRANSACTION_TYPES:
            reasons.append("unsupported_transaction_type")

        if not CURRENCY_CODE_PATTERN.fullmatch(currency):
            reasons.append("invalid_currency_code")

        if status not in ALLOWED_STATUSES:
            reasons.append("unsupported_status")

        if transaction_type in {"transfer", "payment"} and not counterparty_id:
            reasons.append("missing_counterparty_account_id")

        if reasons:
            rejected_transactions.append(
                RejectedTransaction(
                    row_number=row_number,
                    raw_data=raw_data,
                    reasons=reasons,
                )
            )
            continue

        # These values are non-None whenever no validation reason was added.
        assert transaction_date is not None
        assert amount is not None
        valid_transactions.append(
            Transaction(
                transaction_id=transaction_id,
                account_id=account_id,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                amount=amount,
                currency=currency,
                status=status,
                counterparty_account_id=counterparty_id,
            )
        )

    return TransformResult(
        valid_transactions=valid_transactions,
        rejected_transactions=rejected_transactions,
    )

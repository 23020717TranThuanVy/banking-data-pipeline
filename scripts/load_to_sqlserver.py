"""Load the transformed CSV output into SQL Server Express."""

import argparse
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from banking_pipeline.load import load_transactions
from banking_pipeline.transform import Transaction


DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "valid_transactions.csv"


def read_transactions(path: Path) -> list[Transaction]:
    """Read normalized transaction rows created by run_transform.py."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {
            "transaction_id",
            "account_id",
            "transaction_date",
            "transaction_type",
            "amount",
            "currency",
            "status",
            "counterparty_account_id",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Input CSV is missing columns: " + ", ".join(sorted(missing)))

        return [
            Transaction(
                transaction_id=row["transaction_id"],
                account_id=row["account_id"],
                transaction_date=datetime.fromisoformat(row["transaction_date"]),
                transaction_type=row["transaction_type"],
                amount=Decimal(row["amount"]),
                currency=row["currency"],
                status=row["status"],
                counterparty_account_id=row["counterparty_account_id"] or None,
            )
            for row in reader
        ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load transformed CSV into SQL Server.")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Transformed valid-transactions CSV (default: data/processed/valid_transactions.csv)",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    transactions = read_transactions(input_path)
    summary = load_transactions(transactions)
    print(f"Read rows: {len(transactions)}")
    print(f"Inserted rows: {summary.inserted}")
    print(f"Skipped existing rows: {summary.skipped_existing}")


if __name__ == "__main__":
    main()

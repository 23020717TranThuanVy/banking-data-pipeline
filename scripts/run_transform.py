"""Run the sample CSV through the Extract and Transform stages."""

import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from banking_pipeline.extract import DEFAULT_CSV_PATH, extract_transactions
from banking_pipeline.transform import TransformResult, transform_transactions


VALID_COLUMNS = [
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency",
    "status",
    "counterparty_account_id",
]
REJECTED_COLUMNS = ["row_number", "transaction_id", "reasons", "raw_data"]


def resolve_path(value: str) -> Path:
    """Resolve relative paths from the project root, not the shell location."""
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def write_results(output_dir: Path, result: TransformResult) -> tuple[Path, Path]:
    """Write valid and rejected rows as separate UTF-8 CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    valid_path = output_dir / "valid_transactions.csv"
    rejected_path = output_dir / "rejected_transactions.csv"

    with valid_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=VALID_COLUMNS)
        writer.writeheader()
        for transaction in result.valid_transactions:
            row = asdict(transaction)
            row["transaction_date"] = transaction.transaction_date.isoformat()
            row["amount"] = format(transaction.amount, "f")
            writer.writerow(row)

    with rejected_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REJECTED_COLUMNS)
        writer.writeheader()
        for rejected in result.rejected_transactions:
            writer.writerow(
                {
                    "row_number": rejected.row_number,
                    "transaction_id": rejected.raw_data.get("transaction_id", ""),
                    "reasons": ";".join(rejected.reasons),
                    "raw_data": json.dumps(rejected.raw_data, ensure_ascii=False),
                }
            )

    return valid_path, rejected_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and transform mock transactions.")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_CSV_PATH),
        help="Input CSV path (default: data/raw/transactions.csv)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directory for result CSV files (default: data/processed)",
    )
    args = parser.parse_args()

    input_path = resolve_path(args.input)
    output_dir = resolve_path(args.output_dir)
    rows = extract_transactions(input_path)
    result = transform_transactions(rows)
    valid_path, rejected_path = write_results(output_dir, result)

    print(f"Input rows: {len(rows)}")
    print(f"Valid rows: {len(result.valid_transactions)}")
    print(f"Rejected rows: {len(result.rejected_transactions)}")
    print(f"Valid output: {valid_path}")
    print(f"Rejected output: {rejected_path}")
    for rejected in result.rejected_transactions:
        transaction_id = rejected.raw_data.get("transaction_id") or "(empty)"
        print(
            f"  Row {rejected.row_number} [{transaction_id}]: "
            f"{', '.join(rejected.reasons)}"
        )


if __name__ == "__main__":
    main()

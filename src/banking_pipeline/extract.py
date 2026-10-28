"""Đọc dữ liệu giao dịch từ CSV mà chưa biến đổi giá trị của từng dòng."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "transactions.csv"

EXPECTED_COLUMNS = {
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency",
    "status",
    "counterparty_account_id",
}


def extract_transactions(csv_path: str | Path = DEFAULT_CSV_PATH) -> list[dict[str, str]]:
    """Đọc các dòng CSV và trả về danh sách dictionary dạng chuỗi.

    CSV là dữ liệu thô nên module này không đổi kiểu ngày/số tiền và không
    loại bỏ dòng lỗi. Các quy tắc chất lượng sẽ được xử lý ở bước transform.
    Có thể truyền đường dẫn khác để đọc một file CSV khác cùng cấu trúc.
    """
    path = Path(csv_path)

    with path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_columns = set(reader.fieldnames or [])
        missing_columns = EXPECTED_COLUMNS - actual_columns

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV thiếu các cột bắt buộc: {missing}")

        return [dict(row) for row in reader]

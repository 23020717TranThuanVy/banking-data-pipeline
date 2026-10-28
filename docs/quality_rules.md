# Quy tắc chất lượng dữ liệu

Các quy tắc này được áp dụng trong `src/banking_pipeline/transform.py` sau khi đọc CSV:

- Chuẩn hóa khoảng trắng; chuyển mã giao dịch/tài khoản thành chữ hoa, loại giao dịch/trạng thái thành chữ thường và mã tiền tệ thành chữ hoa.
- Bắt buộc có `transaction_id` và `account_id`.
- Ngày phải đọc được bằng định dạng ISO.
- Số tiền phải là số hữu hạn và lớn hơn 0.
- Loại giao dịch được phép: `deposit`, `withdrawal`, `transfer`, `payment`.
- Trạng thái được phép: `completed`, `pending`, `failed`.
- `currency` phải gồm ba chữ cái viết hoa sau chuẩn hóa (ví dụ `VND`).
- `transfer` và `payment` phải có `counterparty_account_id`.
- Trong một lần xử lý file, lần xuất hiện đầu tiên của `transaction_id` được giữ; các lần lặp sau bị từ chối. Cách này xác định rõ dòng nào đại diện cho mã giao dịch trong batch.
- Một dòng có thể có nhiều lý do từ chối. Dữ liệu thô và số dòng tương ứng được giữ lại để tra cứu.

Kết quả hợp lệ dùng `datetime` cho ngày giờ và `Decimal` cho số tiền để tránh sai số số thực nhị phân. Module này không ghi file kết quả hay kết nối database.

## Rejection reason codes

A rejected row may contain one or more of these codes:

- `missing_transaction_id`, `missing_account_id`
- `duplicate_transaction_id` (the first ID occurrence in the batch takes precedence)
- `invalid_transaction_date`
- `amount_not_numeric`, `amount_not_finite`, `non_positive_amount`
- `unsupported_transaction_type`, `unsupported_status`, `invalid_currency_code`
- `missing_counterparty_account_id`

Codes are stable identifiers for downstream reporting; `raw_data` and `row_number` retain enough context to inspect each rejected CSV row.

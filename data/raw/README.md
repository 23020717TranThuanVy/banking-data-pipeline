# Dữ liệu CSV giả lập

`transactions.csv` được soạn thủ công cho mục đích học tập. Tên tài khoản và giao dịch đều là mã giả; không lấy từ ngân hàng hay cá nhân thật.

## Các cột

| Cột | Ý nghĩa |
|---|---|
| `transaction_id` | Mã giao dịch giả lập, dự kiến là khóa nhận diện duy nhất |
| `account_id` | Mã tài khoản nguồn giả lập |
| `transaction_date` | Thời điểm giao dịch theo định dạng ISO `YYYY-MM-DDTHH:MM:SS` |
| `transaction_type` | Loại giao dịch: `deposit`, `withdrawal`, `transfer` hoặc `payment` |
| `amount` | Số tiền giả lập, dùng dấu chấm thập phân |
| `currency` | Mã tiền tệ, ví dụ `VND` |
| `status` | Trạng thái giả lập như `completed`, `pending` hoặc `failed` |
| `counterparty_account_id` | Mã tài khoản đối ứng giả lập; có thể để trống với giao dịch không cần tài khoản đối ứng |

## Các tình huống được cài vào

- 9 dòng đầu là giao dịch hợp lệ mẫu.
- Một dòng thiếu `transaction_id`.
- Một dòng có ngày không phân tích được (`not-a-date`).
- Một dòng có số tiền âm.
- Một dòng thiếu `account_id`.
- Một dòng dùng loại giao dịch ngoài danh sách mẫu (`crypto`).
- Dòng cuối lặp lại `TXN0003` để kiểm tra cách xử lý mã giao dịch trùng.

Các quy tắc phân loại được hiện thực trong `src/banking_pipeline/transform.py` và mô tả tại `docs/quality_rules.md`. Dữ liệu này chỉ là đầu vào mẫu, chưa được xử lý hay nạp vào database.

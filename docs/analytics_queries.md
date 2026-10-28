# Truy vấn SQL phân tích

Mở `sql/analytics.sql` trong VS Code, chọn kết nối và database `BankingTransactions`, rồi chạy từng câu lệnh `SELECT` để xem các result set.

File gồm các phân tích:

1. Số giao dịch, tổng và trung bình amount theo ngày.
2. Khối lượng theo loại giao dịch.
3. Khối lượng theo trạng thái.
4. Top 10 tài khoản nguồn theo số lượng và tổng amount.
5. Chi tiết các giao dịch có trạng thái `failed`.

Trong bộ dữ liệu mẫu, amount luôn dương. Vì chưa có số dư đầu kỳ và quy tắc ghi nợ/ghi có, `SUM(amount)` là tổng giá trị giao dịch, không phải số dư tài khoản. Query theo `account_id` chỉ tính tài khoản nguồn, không tính tài khoản đối ứng.

Dự kiến với dữ liệu hiện tại, tổng `amount` của 9 dòng hợp lệ là 13,819,000.50 VND. Kết quả query phụ thuộc vào database mà extension đang kết nối.

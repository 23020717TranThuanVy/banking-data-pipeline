# Thiết kế tổng quan

Pipeline dự kiến đi theo thứ tự:

1. `data/raw/`: lưu CSV giao dịch giả lập làm dữ liệu đầu vào.
2. `src/banking_pipeline/extract.py`: đọc CSV và đưa dữ liệu thô vào luồng xử lý.
3. `src/banking_pipeline/transform.py`: chuẩn hóa, kiểm tra quy tắc chất lượng, tách bản ghi hợp lệ và bản ghi bị từ chối kèm lý do.
4. `src/banking_pipeline/load.py`: nạp dữ liệu hợp lệ vào SQL Server Express; thiết kế khóa duy nhất để chạy lại không tạo bản ghi trùng.
5. `sql/`: lưu schema và các truy vấn phân tích.
6. `tests/`: kiểm tra quy tắc Python và các luồng tích hợp cần SQL Server.

Thông tin kết nối lấy từ biến môi trường (mẫu tại `.env.example`); không đưa mật khẩu vào mã nguồn hoặc Git. Dữ liệu dùng trong project là dữ liệu giả lập.

Các module hiện chỉ là khung, chưa triển khai xử lý.

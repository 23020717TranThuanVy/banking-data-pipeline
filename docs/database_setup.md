# Hướng dẫn chạy bước SQL Server

`sql/schema.sql` chỉ tạo bảng `dbo.transactions` trong database đang được chọn; script không tạo database. Database mặc định trong `.env.example` là `BankingTransactions`.

## Các bước chuẩn bị trên máy

1. Trong SQL Server Management Studio, kết nối tới `localhost\SQLEXPRESS` bằng Windows Authentication. Tạo database `BankingTransactions` nếu chưa có.
2. Chọn database `BankingTransactions`, mở `sql/schema.sql` và chạy script để tạo bảng.
3. Trong PowerShell tại thư mục gốc project, tạo `.env` từ `.env.example` và kiểm tra thông số server/database. Không commit `.env`.
4. Tạo môi trường Python riêng và cài dependency:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

5. Chạy `python scripts/run_transform.py` để tạo `data/processed/valid_transactions.csv`, sau đó chạy `python scripts/load_to_sqlserver.py`.
6. Chạy lại loader để kiểm tra idempotency: lần đầu dự kiến insert 9 dòng; lần sau dự kiến insert 0 và skip 9 dòng.

Các bước trên chưa được chạy. Chưa cài package, tạo database hay kết nối tới SQL Server trong project này.

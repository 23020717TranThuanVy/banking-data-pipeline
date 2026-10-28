# banking-data-pipeline

Project học Data Engineering bằng Python và SQL Server Express, sử dụng dữ liệu giao dịch giả lập.

## Pipeline hiện có

1. Đọc CSV từ `data/raw/transactions.csv`.
2. Kiểm tra cấu trúc CSV, chuẩn hóa dữ liệu và tách dòng hợp lệ/không hợp lệ.
3. Ghi kết quả vào `data/processed/valid_transactions.csv` và `data/processed/rejected_transactions.csv`. File bị từ chối có mã lý do và dữ liệu gốc.
4. Nạp dòng hợp lệ vào SQL Server Express. `transaction_id` là khóa chính; chạy lại sẽ bỏ qua mã đã có.
5. Chạy truy vấn phân tích trong `sql/analytics.sql`.
6. Kiểm tra logic bằng pytest.

Dữ liệu mẫu có 15 dòng: 9 hợp lệ và 6 dòng bị từ chối, bao gồm một giao dịch trùng mã. Đây đều là dữ liệu giả lập.

## Cấu trúc thư mục

```text
banking-data-pipeline/
├── data/
│   ├── raw/                  # CSV giả lập và mô tả dữ liệu
│   └── processed/            # CSV đầu ra; được Git bỏ qua
├── docs/                     # Kiến trúc, quy tắc chất lượng, hướng dẫn SQL
├── scripts/
│   ├── run_transform.py      # Chạy Extract + Transform và ghi hai CSV đầu ra
│   └── load_to_sqlserver.py  # Nạp CSV hợp lệ vào SQL Server
├── sql/
│   ├── schema.sql            # Tạo bảng dbo.transactions trong database đã chọn
│   └── analytics.sql         # Truy vấn phân tích
├── src/banking_pipeline/     # Module extract, transform, load
├── tests/
│   ├── fixtures/             # CSV nhỏ dùng trong unit test
│   ├── integration/          # Dành cho test tích hợp trong tương lai
│   └── unit/                 # Test Extract, Transform và logic Loader giả lập
├── .env.example              # Mẫu cấu hình kết nối, không chứa mật khẩu
├── pyproject.toml            # Metadata và cấu hình pytest
└── requirements.txt          # Thư viện project
```

## Yêu cầu

- Python 3.10 trở lên.
- SQL Server Express và ODBC Driver for SQL Server.
- VS Code cùng extension SQL Server (`mssql`) để chạy và xem truy vấn SQL.

## Thiết lập lần đầu

Mở PowerShell tại thư mục gốc project. Tạo và kích hoạt môi trường Python riêng, rồi cài dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example` nếu chưa có:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Cấu hình mẫu dùng Windows Authentication, server `localhost\SQLEXPRESS` và database `BankingTransactions`. Điều chỉnh `.env` nếu máy bạn dùng giá trị khác. Không commit `.env` lên Git.

Database `BankingTransactions` cần tồn tại trước. `sql/schema.sql` chỉ tạo bảng `dbo.transactions`, không tạo database. Xem [database_setup.md](docs/database_setup.md) để biết các bước SQL Server.

## Chạy pipeline

Khi `.venv` đang được kích hoạt và database/bảng đã sẵn sàng, chạy từ thư mục gốc:

```powershell
python scripts/run_transform.py
python scripts/load_to_sqlserver.py
```

Kết quả Transform nằm trong `data/processed/`. Với dữ liệu mẫu, loader nạp 9 dòng ở lần đầu; chạy lại sẽ bỏ qua các dòng đã có.

Để chạy truy vấn phân tích, mở `sql/analytics.sql` trong VS Code, kết nối tới `BankingTransactions` bằng extension `mssql`, rồi chọn **Run**. `SUM(amount)` là tổng giá trị giao dịch, không phải số dư ròng.

## Chạy pytest

Trong môi trường `.venv`, chạy:

```powershell
python -m pytest
```

Unit test bao phủ Extract, Transform, cấu hình connection string và logic insert/skip với fake connection. Các test không kết nối SQL Server thật; tính idempotent trên SQL Server đã được xác nhận riêng bằng cách chạy loader hai lần.

## Ghi chú

- `.env`, `.venv/` và các file sinh trong `data/processed/` không được commit.
- Docker không cần cho phiên bản hiện tại; Python và SQL Server chạy trực tiếp trên Windows.
# banking-data-pipeline

Dự án học Data Engineering: pipeline xử lý giao dịch ngân hàng giả lập bằng Python, SQL Server Express, SQL và pytest.

## Mục tiêu

CSV giả lập → Python Extract → Transform và kiểm tra chất lượng dữ liệu → SQL Server Express → truy vấn phân tích → kiểm thử.

Dự án sẽ phân loại bản ghi hợp lệ và không hợp lệ, lưu lý do từ chối, hỗ trợ nạp lại dữ liệu an toàn và không lưu thông tin đăng nhập trong mã nguồn.

## Cấu trúc hiện tại

```text
banking-data-pipeline/
├── data/
│   ├── raw/                 # CSV đầu vào (dữ liệu giả lập)
│   └── processed/           # Kết quả xử lý được tạo khi chạy pipeline
├── docs/                    # Tài liệu thiết kế và hướng dẫn
├── sql/                     # Script tạo bảng và truy vấn phân tích
├── src/banking_pipeline/    # Các module Python của pipeline
├── tests/
│   ├── unit/                # Kiểm thử từng hàm/module
│   └── integration/         # Kiểm thử tích hợp với SQL Server
├── .env.example             # Mẫu cấu hình, không chứa thông tin đăng nhập
├── pyproject.toml           # Metadata và cấu hình công cụ Python
└── requirements.txt         # Các thư viện Python cần cài
```

## Các giai đoạn

1. Khung project (đã tạo).
2. CSV giao dịch giả lập.
3. Extract, transform và kiểm tra chất lượng dữ liệu.
4. Nạp dữ liệu vào SQL Server Express theo cách chạy lại an toàn.
5. Truy vấn SQL phân tích.
6. Kiểm thử bằng pytest và chạy thử toàn pipeline.

Hiện tại đây mới là khung thư mục và cấu hình ban đầu; các module chưa có logic xử lý.

## Cấu hình kết nối

Khi triển khai phần nạp dữ liệu, sao chép `.env.example` thành `.env` và cập nhật giá trị phù hợp trên máy. Không commit `.env` hoặc thông tin đăng nhập lên GitHub.

## Cài thư viện (khi bắt đầu triển khai pipeline)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Các lệnh trên chỉ là hướng dẫn; môi trường hiện tại chưa được thay đổi và thư viện chưa được cài.

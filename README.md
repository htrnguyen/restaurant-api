# Hệ thống Quản lý Nhà hàng - API Documentation

Hệ thống quản lý nhà hàng được xây dựng theo kiến trúc microservices với 6 service chính:

-   **User Service (8001)**: Quản lý người dùng và xác thực
-   **Table Service (8002)**: Quản lý bàn và đặt bàn
-   **Menu Service (8003)**: Quản lý thực đơn và món ăn
-   **Order Service (8004)**: Quản lý đơn hàng
-   **Kitchen Service (8005)**: Quản lý bếp và chế biến
-   **Payment Service (8006)**: Quản lý thanh toán và hóa đơn

## Yêu cầu hệ thống

-   Python 3.9+
-   Docker và Docker Compose (nếu chạy bằng Docker)
-   PostgreSQL (đã được cấu hình trong Supabase)

## Cách 1: Chạy bằng Docker

1. Clone repository:

```bash
git clone <repository-url>
cd restaurant-api
```

2. Tạo file .env trong thư mục gốc với các biến môi trường:

```env
SUPABASE_URL=https://ziursewxdahtbrjxdaqo.supabase.co
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

3. Build và chạy các containers:

```bash
docker-compose up --build
```

Các service sẽ được khởi chạy ở các cổng tương ứng:

-   User Service: http://localhost:8001
-   Table Service: http://localhost:8002
-   Menu Service: http://localhost:8003
-   Order Service: http://localhost:8004
-   Kitchen Service: http://localhost:8005
-   Payment Service: http://localhost:8006

Để dừng các containers:

```bash
docker-compose down
```

## Cách 2: Chạy trực tiếp bằng Python

1. Clone repository và cài đặt dependencies:

```bash
git clone <repository-url>
cd restaurant-api
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. Tạo file .env trong thư mục gốc với các biến môi trường (tương tự như trên)

3. Chạy tất cả các service cùng lúc:

```bash
python run_services.py
```

Hoặc chạy từng service riêng lẻ:

```bash
# User Service
cd services/user-service
uvicorn app.main:app --reload --port 8001

# Table Service
cd services/table-service
uvicorn app.main:app --reload --port 8002

# Menu Service
cd services/menu-service
uvicorn app.main:app --reload --port 8003

# Order Service
cd services/order-service
uvicorn app.main:app --reload --port 8004

# Kitchen Service
cd services/kitchen-service
uvicorn app.main:app --reload --port 8005

# Payment Service
cd services/payment-service
uvicorn app.main:app --reload --port 8006
```

## Chạy API Documentation Server

Sau khi đã khởi động các services, bạn có thể chạy API Documentation server để xem giao diện tổng quan các API:

```bash
python -m uvicorn api_docs:app --reload
```

API Documentation sẽ chạy tại http://localhost:8000, cung cấp:

-   Giao diện trực quan hiển thị tất cả các services
-   Trạng thái hoạt động của từng service
-   Danh sách các endpoints chính của mỗi service
-   Link trực tiếp đến Swagger UI của từng service

## Kiểm tra hoạt động

1. Mở trình duyệt và truy cập trang API documentation:

```
http://localhost:8000
```

2. Kiểm tra health check của từng service:

-   http://localhost:8001/health
-   http://localhost:8002/health
-   http://localhost:8003/health
-   http://localhost:8004/health
-   http://localhost:8005/health
-   http://localhost:8006/health

3. Truy cập Swagger documentation của từng service:

-   http://localhost:8001/docs
-   http://localhost:8002/docs
-   http://localhost:8003/docs
-   http://localhost:8004/docs
-   http://localhost:8005/docs
-   http://localhost:8006/docs

## Testing

Chạy các test case tự động:

```bash
python test_api_vi.py
```

## Troubleshooting

1. Nếu gặp lỗi khi chạy Docker:

-   Kiểm tra Docker daemon đã chạy chưa
-   Kiểm tra ports có bị conflict không
-   Xem logs: `docker-compose logs`

2. Nếu gặp lỗi khi chạy trực tiếp:

-   Kiểm tra Python version
-   Kiểm tra virtual environment đã được activate
-   Kiểm tra tất cả dependencies đã được cài đặt
-   Kiểm tra file .env có đúng format và đầy đủ thông tin

## Dừng hệ thống

-   Nếu chạy bằng Docker: `docker-compose down`
-   Nếu chạy trực tiếp: Nhấn Ctrl+C trong terminal đang chạy run_services.py
